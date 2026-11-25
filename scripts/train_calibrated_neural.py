"""보정 신경 초파리 상대 SAC 조준기와 고정 조준기 상대 LIF 배율 학습."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from flytracker.env import ENV_VERSION
from flytracker.neural_training import calibrated_config, WeightedEnv, GroupedWeights, PROFILE_ID, DATA_SHA256
from flytracker.players import baseline_player,PolicyPlayer
from flytracker.wrappers import TrackingAssist
from flytracker.aimer_training_env import RuleFireTraining

def write(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+".tmp")
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    temp.replace(p)
def stamp():
    return datetime.now(timezone.utc).isoformat()
def progress(out,phase,**data):
    row=dict(phase=phase,utc=stamp(),**data)
    write(out/"progress.json",row)
    print(json.dumps(row,ensure_ascii=False),flush=True)

class Build:
    def __init__(self,cfg,rule_fire=False): self.cfg=cfg; self.rule_fire=rule_fire
    def __call__(self):
        from stable_baselines3.common.monitor import Monitor
        env=WeightedEnv(self.cfg)
        return Monitor(RuleFireTraining(env,assist=.05) if self.rule_fire else TrackingAssist(env,.05))

def episode(cfg,seed,model=None,weights=None,passive=False):
    env=WeightedEnv(cfg,weights)
    player=baseline_player(cfg)
    model_player=(PolicyPlayer(model,assist=.05,tracker=player.policy,
        rule_fire=model.action_space.shape==(2,),strip_shot=False) if model is not None else None)
    obs,_=env.reset(seed=int(seed)); player.reset()
    total=0.; steps=0; speeds=[]; heights=[]
    try:
        while True:
            if passive: action=np.array([0.,0.,-1.])
            elif model is None: action=player.act(obs)
            else:action=model_player.act(obs)
            obs,reward,term,trunc,info=env.step(action)
            total+=reward; steps+=1
            speeds.append(env.fly.speed); heights.append(float(env.fly.pos[1]))
            if not (np.isfinite(obs).all() and np.isfinite(env.fly.pos).all()
                    and np.isfinite(env.fly.velocity).all() and np.isfinite(env.fly.quaternion).all()
                    and np.isfinite(env.fly.angular_velocity).all() and np.isfinite(env.fly.sim.neural.pending).all()):
                raise ValueError("Nonfinite neural flight")
            if term or trunc: break
        diag=env.fly.diagnostics()
        ticks=max(1,round(info["t"]/.005))
        correction=diag["boundary_corrections"]/ticks
        warning=env.fly.speed_warning_steps/ticks
        duration=float(info["t"])
        return dict(seed=int(seed),stimulus=cfg.stimulus.enabled,captured=bool(info["captured"]),
            seconds=duration,shots=info["shots"],misfires=info["misfires"],return_=float(total),
            events=info["stimulus"]["event_count"],escapeTransitions=sum(x["phase"]=="escape" for x in env.fly.phase_events),
            boundaryCorrections=diag["boundary_corrections"],warningFraction=warning,
            angularWarningSteps=env.fly.angular_warning_steps,meanSpeed=float(np.mean(speeds)),minHeight=min(heights),
            fitness=duration/cfg.max_seconds-.05*correction-.05*warning,
            scoreAimer=float(info["captured"])+.1*(1-duration/cfg.max_seconds),
            scoreFly=duration/cfg.max_seconds,steps=steps)
    finally: env.close()

_MODEL=None
def worker_init(path):
    global _MODEL
    import torch
    torch.set_num_threads(1)
    from stable_baselines3 import SAC
    _MODEL=SAC.load(path,device="cpu")
def score_task(payload):
    cfg,seed,weights=payload
    return episode(cfg,seed,_MODEL,weights)

def evaluate(out,name,cfg,seeds,model=None,weights=None,passive=False):
    rows=[episode(cfg,s,model,weights,passive) for s in seeds]
    write(out/(name+".json"),rows)
    progress(out,name,episodes=len(rows),captures=sum(r["captured"] for r in rows),
        meanSeconds=float(np.mean([r["seconds"] for r in rows])))
    return rows

def bootstrap(base,candidate,key):
    a=np.array([x[key] for x in base]); b=np.array([x[key] for x in candidate])
    if [x["seed"] for x in base]!=[x["seed"] for x in candidate]:
        raise ValueError("Paired seeds differ")
    rng=np.random.default_rng(20261120)
    delta=(b-a)[rng.integers(len(a),size=(10000,len(a)))].mean(axis=1)
    return dict(baseline=float(a.mean()),candidate=float(b.mean()),
        probability=float(np.mean(delta>0)+.5*np.mean(delta==0)),
        delta95=np.quantile(delta,[.025,.975]).tolist(),pairedEpisodes=len(a))


def initialize_from_baseline(model,cfg,out):
    """학습용 seed에서만 관측 기반 기준선의 탐색과 발사를 지도 학습한다."""
    import torch
    observations=[]; targets=[]
    env=WeightedEnv(cfg); teacher=baseline_player(cfg)
    for seed in range(1000,1016):
        obs,_=env.reset(seed=seed);teacher.reset()
        while True:
            action=teacher.act(obs)
            target=np.array(action,copy=True)
            if obs[0]>.5:target[:2]=0.  # TrackingAssist already provides visible tracking.
            observations.append(obs.copy());targets.append(target[:model.action_space.shape[0]])
            obs,_,term,trunc,_=env.step(action)
            if term or trunc:break
    env.close()
    x=torch.as_tensor(np.array(observations),device=model.device)
    y=torch.as_tensor(np.array(targets),dtype=torch.float32,device=model.device)
    rng=np.random.default_rng(42)
    model.policy.set_training_mode(True)
    for _ in range(1000):
        ids=rng.integers(len(x),size=256)
        mean,_,_=model.policy.actor.get_action_dist_params(x[ids])
        loss=torch.nn.functional.mse_loss(torch.tanh(mean),y[ids])
        model.policy.actor.optimizer.zero_grad()
        loss.backward();model.policy.actor.optimizer.step()
    write(out/"imitation-initialization.json",dict(seedStart=1000,episodes=16,samples=len(x),
        updates=1000,finalLoss=float(loss.detach().cpu()),teacher="observable RuleAimer",
        note="imitation initialization followed by SAC; not reinforcement learning from scratch"))

def run(out,steps,workers,gens,seconds,device,max_train_seconds,learning_starts=2000,rule_fire=False):
    import torch
    from stable_baselines3 import SAC
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.vec_env import SubprocVecEnv
    torch.set_num_threads(1)
    if out.exists(): raise FileExistsError(out)
    out.mkdir(parents=True)
    cfg=calibrated_config(max_seconds=seconds)
    write(out/"config.json",dict(envVersion=ENV_VERSION,env=cfg.to_dict(),side="aimer",
        algo=dict(name="sac",assist=.05,frameStack=1,steps=steps,seed=42,learningStarts=learning_starts,trainingDevice=device,evaluationDevice="cpu",fireMode="rule" if rule_fire else "policy"),
        profile=dict(id=PROFILE_ID,dataSha256=DATA_SHA256,previousGatePassed=False),
        circuitTraining=dict(generations=gens,pairs=4,seedsPerGeneration=2,logSigma=.12,
            learningRate=.08,positiveGainRange=[.5,2],selection="dev 20000..20003"),
        conditions=dict(codexRemainingStopBelow=5,budgetUSD=3,beamRadius=.00125,holdSeconds=.15)))
    start=time.monotonic()
    progress(out,"preflight",torch=torch.__version__,numpy=np.__version__,cuda=torch.cuda.is_available(),
        device=device,workers=workers)
    probe=WeightedEnv(cfg); probe.reset(seed=42)
    identity=GroupedWeights.identity(probe); identity.save(out/"identity.npz")
    write(out/"contract.json",identity.signature); probe.close()
    bases={}
    for enabled in (False,True):
        sub=replace(cfg,stimulus=replace(cfg.stimulus,enabled=enabled))
        bases[enabled]=evaluate(out,"aimer-baseline-"+str(enabled),sub,range(30000,30012))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("aimer-baseline-*.json")}
    write(out/"baseline-freeze.json",dict(utc=stamp(),sha256=hashes))
    if (out.parent/"STOP").exists(): raise InterruptedError("STOP before training")
    vec=SubprocVecEnv([Build(cfg,rule_fire) for _ in range(workers)],start_method="spawn")
    class Watch(BaseCallback):
        def __init__(self): super().__init__(); self.last=0; self.saved=0; self.started=time.monotonic()
        def _on_step(self):
            if self.num_timesteps-self.last>=1000:
                progress(out,"aimer-training",steps=self.num_timesteps,
                    seconds=round(time.monotonic()-self.started,2))
                self.last=self.num_timesteps
            if self.num_timesteps-self.saved>=10000:
                self.model.save(out/("step-%07d.zip"%self.num_timesteps))
                self.saved=self.num_timesteps
            return not (out.parent/"STOP").exists() and time.monotonic()-self.started<max_train_seconds
    try:
        model=SAC("MlpPolicy",vec,seed=42,device=device,learning_starts=learning_starts,
            buffer_size=200000,batch_size=256,train_freq=(1,"step"),gradient_steps=1,
            ent_coef=.0001,policy_kwargs=dict(net_arch=[128,128],log_std_init=-4),verbose=0)
        with torch.no_grad():
            model.policy.actor.mu.weight.zero_()
            model.policy.actor.mu.bias.zero_()
            if not rule_fire:model.policy.actor.mu.bias[2]=2.
            model.policy.actor.log_std.weight.zero_()
            model.policy.actor.log_std.bias.fill_(-4.)
        progress(out,"imitation-initialization")
        initialize_from_baseline(model,cfg,out)
        before=model.policy.actor.mu.weight.detach().cpu().numpy().copy()
        model.learn(total_timesteps=steps,callback=Watch())
        model.save(out/"model.zip")
        actorChanged=not np.array_equal(before,model.policy.actor.mu.weight.detach().cpu().numpy())
        write(out/"aimer-training.json",dict(timesteps=model.num_timesteps,actorChanged=actorChanged,
            elapsedSeconds=time.monotonic()-start,requestedSteps=steps,stoppedEarly=model.num_timesteps<steps))
    finally: vec.close()
    model=SAC.load(out/"model.zip",device="cpu")
    results={}
    for enabled in (False,True):
        sub=replace(cfg,stimulus=replace(cfg.stimulus,enabled=enabled))
        rows=evaluate(out,"aimer-final-"+str(enabled),sub,range(30000,30012),model)
        results[str(enabled)]=bootstrap(bases[enabled],rows,"scoreAimer")
    write(out/"aimer-verdict.json",results)
    if (out.parent/"STOP").exists():
        progress(out,"stopped",reason="STOP after checkpoint"); return
    # dev 조건에서 포획 가능한 상대인지 확인한다. 약한 상대 때문에 생존 점수가 평평하면 학습 성과로 표시하지 않는다.
    dev=evaluate(out,"fixed-aimer-dev",cfg,range(20000,20004),model)
    fixedhash=hashlib.sha256((out/"model.zip").read_bytes()).hexdigest()
    beforefly={}
    for enabled in (False,True):
        sub=replace(cfg,stimulus=replace(cfg.stimulus,enabled=enabled))
        beforefly[enabled]=evaluate(out,"fly-baseline-"+str(enabled),sub,range(40000,40012),model,identity)
    write(out/"fly-baseline-freeze.json",dict(modelSha256=fixedhash,sha256={
        p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("fly-baseline-*.json")}))
    free_cfg=replace(cfg,stimulus=replace(cfg.stimulus,enabled=False))
    free_baseline=evaluate(out,"freeflight-baseline",free_cfg,range(60000,60006),weights=identity,passive=True)
    if not any(r["captured"] for r in dev):
        progress(out,"completed",circuitSkipped="fixed aimer captured 0/4 dev episodes",
            elapsedSeconds=time.monotonic()-start)
        return
    theta=identity; rng=np.random.default_rng(314); best=theta
    best_score=float(np.mean([r["fitness"] for r in dev]))
    history=[]
    with ProcessPoolExecutor(workers,initializer=worker_init,initargs=(str(out/"model.zip"),)) as pool:
        for gen in range(gens):
            if (out.parent/"STOP").exists(): break
            noise=rng.normal(size=(4,len(theta.theta)))
            seeds=rng.integers(1000,9000,size=2).tolist()
            variants=[theta.updated(theta.theta+sign*.12*n) for n in noise for sign in (1,-1)]
            rows=list(pool.map(score_task,[(cfg,s,w) for w in variants for s in seeds]))
            rewards=np.array([np.mean([r["fitness"] for r in rows[i*2:(i+1)*2]]) for i in range(8)])
            delta=rewards[::2]-rewards[1::2]
            scale=max(float(np.std(rewards)),1e-6)
            gradient=np.mean(delta[:,None]*noise,axis=0)/(2*.12*scale)
            theta=theta.updated(theta.theta+.08*gradient-.002*theta.theta)
            validation=list(pool.map(score_task,[(cfg,s,theta) for s in range(20000,20004)]))
            score=float(np.mean([r["fitness"] for r in validation]))
            theta.save(out/("weights-gen-%02d.npz"%gen),dict(devFitness=score,seeds=seeds))
            if score>best_score: best,best_score=theta,score
            history.append(dict(generation=gen,meanFitness=float(rewards.mean()),
                rewardSpread=float(rewards.std()),devFitness=score,nonzeroPairs=int(np.count_nonzero(delta)),
                changedGroups=int(np.count_nonzero(theta.theta))))
            write(out/"circuit-history.json",history)
            progress(out,"circuit-training",**history[-1])
    best.save(out/"weights-selected.npz",dict(devFitness=best_score,selection="dev only"))
    if hashlib.sha256((out/"model.zip").read_bytes()).hexdigest()!=fixedhash:
        raise ValueError("Fixed opponent changed")
    verdict={}
    for enabled in (False,True):
        sub=replace(cfg,stimulus=replace(cfg.stimulus,enabled=enabled))
        after=evaluate(out,"fly-final-"+str(enabled),sub,range(40000,40012),model,best)
        verdict[str(enabled)]=bootstrap(beforefly[enabled],after,"scoreFly")
    free_final=evaluate(out,"freeflight-final",free_cfg,range(60000,60006),weights=best,passive=True)
    healthy=all(b["boundaryCorrections"]<=a["boundaryCorrections"] and b["warningFraction"]==0 and b["angularWarningSteps"]==0 for a,b in zip(free_baseline,free_final))
    write(out/"circuit-verdict.json",dict(comparisons=verdict,freeFlightHealthPassed=healthy,biologicalFlightValidated=False,changedGroups=int(np.count_nonzero(best.theta)),
        fixedAimerSha256=fixedhash,selectedWeightsSha256=best.sha256))
    progress(out,"completed",elapsedSeconds=time.monotonic()-start)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--steps",type=int,default=200000)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--learning-starts",type=int,default=2000)
    p.add_argument("--generations",type=int,default=8)
    p.add_argument("--seconds",type=float,default=10)
    p.add_argument("--device",default="cuda")
    p.add_argument("--rule-fire",action="store_true",help="Learn aim with current observations; use the baseline fire rule")
    p.add_argument("--max-train-seconds",type=int,default=2400)
    a=p.parse_args()
    if min(a.steps,a.workers,a.seconds,a.max_train_seconds)<=0 or min(a.generations,a.learning_starts)<0:
        p.error("steps/workers/seconds/time must be positive; generations/learning-starts nonnegative")
    try: run(a.output,a.steps,a.workers,a.generations,a.seconds,a.device,a.max_train_seconds,a.learning_starts,a.rule_fire)
    except BaseException as exc:
        progress(a.output,"error",error=repr(exc))
        raise
if __name__=="__main__": main()
