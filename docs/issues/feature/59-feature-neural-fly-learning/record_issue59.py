"""Record Issue #59 viewer samples using the original validated checkpoints."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path

from flytracker.env import ENV_VERSION, EnvConfig
from flytracker.free_flight import record_free_flight
from flytracker.neural_fly import NeuralConfig
from flytracker.neural_training import GroupedWeights, WeightedEnv
from flytracker.players import baseline_player, load_opponent
from flytracker.record import EpisodeRecorder, RunStore, publish_run


ROOT = Path(__file__).resolve().parents[4]
ISSUE = {"number": 59, "title": "신경회로 초파리 학습",
         "url": "https://github.com/SMU-ReinforementLearning/FlyTracker/issues/59"}
ARTIFACT_HASHES = {
    "model.zip": "0a3b7a30f6b2bbc851f8e9ef9f45fac7fdf4f615880c6dabfaf44ba792c65bc1",
    "weights-selected.npz": "54f75dd01b54d3e90bcbefc93d70014020ec96aa3c7b86c737976e372583412f",
    "config.json": "dc5ef20d4c53aa55767ca9260241ce4f0a8608e1d422d58e079f02d6a5b7153d",
}


def gate():
    (ROOT / "docs/issues/feature/59-feature-neural-fly-learning.md").read_text(encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def record_match(cfg, seed, player, weights, algo, passive=False):
    meta = {"policy": algo}
    if passive:
        meta.update(aimerEnabled=False, captureEnabled=False, mode="free-flight")
    recorder = EpisodeRecorder(WeightedEnv(cfg, weights), meta=meta)
    try:
        if player is not None:
            player.reset()
        obs, _ = recorder.reset(seed=seed)
        while True:
            action = [0, 0, -1] if passive else player.act(obs)
            obs, _, done, truncated, _ = recorder.step(action)
            if done or truncated:
                break
        ep = recorder.last_episode
        if passive:
            ep["summary"].update(mode="free-flight", result="observation_complete")
            ep["frames"]["flySpeed"] = [sum(v*v for v in d["velocity"])**.5 for d in ep["frames"]["neuralDiagnostics"]]
        return ep
    finally:
        recorder.close()


def save(store, published, name, slug, cfg, algo, notes, episodes, extra):
    gate()
    run = store.create_run(slug, algo["name"], "continuous",
                           {"env": cfg.to_dict(), "algo": algo, **extra}, notes)
    for episode in episodes:
        gate()
        run.save_episode(episode, slug)
    gate()
    publish_run(store.root, run.id, published, extra={"issue": ISSUE, "author": "heohs", "name": name})
    print(run.id, [(ep["meta"]["seed"], ep["summary"]["duration"], ep["summary"]["captured"],
                   ep["diagnostics"]["finalNeural"]["boundary_corrections"]) for ep in episodes], flush=True)


def compare_to_training(ep, expected):
    actual = [ep["summary"]["captured"], ep["summary"]["duration"],
              ep["diagnostics"]["finalNeural"]["boundary_corrections"]]
    target = [expected["captured"], expected["seconds"], expected["boundaryCorrections"]]
    ep["meta"]["referenceEvaluation"] = dict(platform="Vast.ai Linux", captured=target[0],
                                             duration=target[1], boundaryCorrections=target[2],
                                             replayMatched=actual == target)
    if actual != target:
        print(f"Replay differs for seed {expected['seed']}: local {actual}, remote {target}", flush=True)


def run(training, recordings, published, resume=False):
    if any(os.environ.get(name) for name in ("FLYTRACKER_NEURAL_SOURCE", "FLYTRACKER_NEURAL_DATA")):
        raise ValueError("Use bundled neural data to record public runs.")
    for name, expected in ARTIFACT_HASHES.items():
        if hashlib.sha256((training / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unexpected original checkpoint hash: {name}")
    saved = read_json(training / "config.json")
    if saved["envVersion"] != ENV_VERSION:
        raise ValueError("Recording requires the original environment version.")
    cfg = EnvConfig.from_dict(saved["env"])
    weights = GroupedWeights.load(training / "weights-selected.npz")
    store = RunStore(recordings)
    if store.root.exists() and not resume:
        raise FileExistsError(store.root)
    import torch
    torch.set_num_threads(1)

    def already_published(slug):
        return resume and any(path.is_dir() and path.name.endswith("_"+slug)
                              for path in published.glob("*_"+slug))
    sac = {**saved["algo"], "side": "aimer", "fire": "rule", "trainedEnvVersion": ENV_VERSION,
           "model": "issue59-sac-300000", "modelSha256": ARTIFACT_HASHES["model.zip"]}
    baseline = {"name": "rule-baseline"}
    no_stimulus = replace(cfg, stimulus=replace(cfg.stimulus, enabled=False))
    free = replace(no_stimulus, capture_enabled=False)
    original_free = replace(free, neural=NeuralConfig(profile_id="original"))
    for state, label, settings in (("original", "기존 비행계수", original_free),
                                    ("calibrated", "실측으로 보정한 비행계수", free)):
        if already_published(f"issue59-free-{state}"):
            continue
        episodes = [record_free_flight(settings, seed) for seed in range(3)]
        save(store, published, label + " 자유비행", f"issue59-free-{state}", settings,
             {"name": "free-flight"}, "seed 0~2, 10초, 조준기 없음", episodes,
             {"evaluation": {"purpose": "profile demonstration"}})

    for enabled, settings in ((False, no_stimulus), (True, cfg)):
        suffix = "gaze" if enabled else "no-stimulus"
        label = "시선 자극 켬" if enabled else "가상 자극 끔"
        for learned, name, algo in ((False, "규칙 조준기", baseline), (True, "학습용 SAC 조준기", sac)):
            if already_published(f"issue59-aimer-{'sac' if learned else 'rule'}-{suffix}"):
                continue
            expected = read_json(training / f"aimer-{'final' if learned else 'baseline'}-{enabled}.json")[:3]
            player = load_opponent(str(training), "aimer", settings).player if learned else baseline_player(settings)
            episodes = [record_match(settings, row["seed"], player, None, algo["name"]) for row in expected]
            for episode, row in zip(episodes, expected):
                compare_to_training(episode, row)
            save(store, published, f"{name} ({label})",
                 f"issue59-aimer-{'sac' if learned else 'rule'}-{suffix}", settings, algo,
                 "보정 초파리 배율 1, 평가 seed 30000~30002", episodes,
                 {"evaluation": {"flyWeights": "original"}})
        player = load_opponent(str(training), "aimer", settings).player
        for name, applied in (("baseline", None), ("final", weights)):
            if already_published(f"issue59-fly-{name}-{suffix}"):
                continue
            label_weights = "원래 가중치" if applied is None else "학습 가중치 후보"
            expected = read_json(training / f"fly-{name}-{enabled}.json")[:3]
            episodes = [record_match(settings, row["seed"], player, applied, "sac") for row in expected]
            for episode, row in zip(episodes, expected):
                compare_to_training(episode, row)
            save(store, published, f"고정 조준기 상대 {label_weights} ({label})",
                 f"issue59-fly-{name}-{suffix}", settings, sac, "평가 seed 40000~40002", episodes,
                 {"evaluation": {"flyWeights": name, "weightsSha256": applied.sha256 if applied else None,
                                 "candidateAdopted": False}})

    # Reproduce the failed free-flight check with exactly the original reset path.
    for name, applied in (("baseline", None), ("final", weights)):
        if already_published(f"issue59-boundary-{name}"):
            continue
        expected = next(row for row in read_json(training / f"freeflight-{name}.json") if row["seed"] == 60001)
        ep = record_match(no_stimulus, expected["seed"], None, applied, "free-flight", passive=True)
        compare_to_training(ep, expected)
        label = "원래 가중치" if applied is None else "학습 가중치 후보"
        save(store, published, f"{label} 자유비행 경계 검사", f"issue59-boundary-{name}",
             free, {"name": "free-flight"}, "무자극·무발사, seed 60001", [ep],
             {"evaluation": {"flyWeights": name, "weightsSha256": applied.sha256 if applied else None,
                             "candidateAdopted": False}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("training", type=Path)
    parser.add_argument("--recordings", type=Path, required=True)
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--resume", action="store_true", help="Skip already published Issue #59 runs")
    args = parser.parse_args()
    run(args.training, args.recordings, args.published, args.resume)


if __name__ == "__main__":
    main()
