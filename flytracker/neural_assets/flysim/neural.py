"""Small connectome-based LIF assay; no body or sensory model."""
import csv, math, time
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

@dataclass(frozen=True)
class Parameters:
    dt_ms: float = .1
    tau_mem_ms: float = 20.
    tau_syn_ms: float = 5.
    rest_mv: float = -52.
    threshold_mv: float = -45.
    refractory_ms: float = 2.2
    delay_ms: float = 1.8
    weight_mv: float = .275
    stimulus_jump_mv: float = 68.75
    stimulus_hz: float = 150.
    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()): raise ValueError('Nonfinite parameter')
        if min(self.dt_ms,self.tau_mem_ms,self.tau_syn_ms,self.delay_ms)<=0: raise ValueError('Invalid time')
        if self.tau_mem_ms==self.tau_syn_ms: raise ValueError('Equal taus unsupported')
        if min(self.refractory_ms,self.weight_mv,self.stimulus_jump_mv,self.stimulus_hz)<0: raise ValueError('Negative parameter')
        if self.threshold_mv<=self.rest_mv: raise ValueError('Invalid threshold')
        for x in (self.delay_ms,self.refractory_ms):
            if not math.isclose(x/self.dt_ms,round(x/self.dt_ms),abs_tol=1e-8): raise ValueError('Noninteger timing')

class Circuit:
    def __init__(self,nodes,edges):
        self.nodes=nodes; self.ids=[r['id'] for r in nodes]
        if not self.ids or len(set(self.ids))!=len(self.ids): raise ValueError('Invalid IDs')
        if len({(e['pre'],e['post']) for e in edges})!=len(edges): raise ValueError('Duplicate edges')
        idx={root:i for i,root in enumerate(self.ids)}
        self.pre=np.array([idx[e['pre']] for e in edges],dtype=np.int32)
        self.post=np.array([idx[e['post']] for e in edges],dtype=np.int32)
        count=np.array([int(e['synapse_count']) for e in edges]); sign=np.array([int(e['source_model_sign']) for e in edges])
        if np.any(count<=0) or not np.all(np.isin(sign,[-1,1])): raise ValueError('Invalid counts/signs')
        self.signed_counts=(count*sign).astype(float)
    @classmethod
    def load(cls,path):
        with (Path(path)/'neurons.csv').open(encoding='utf-8') as f: nodes=list(csv.DictReader(f))
        with (Path(path)/'edges.csv').open(encoding='utf-8') as f: edges=list(csv.DictReader(f))
        return cls(nodes,edges)
    def group(self,prefix): return [i for i,r in enumerate(self.nodes) if r['cell_type'].startswith(prefix)]
    def simulate(self,stimulated=(),duration_ms=1000.,seed=0,params=None,disconnected=False,silenced=()):
        p=params or Parameters(); ratio=duration_ms/p.dt_ms
        if not math.isfinite(ratio) or ratio<=0 or not math.isclose(ratio,round(ratio),abs_tol=1e-7): raise ValueError('Invalid duration')
        n=len(self.ids); steps=round(ratio); delay=round(p.delay_ms/p.dt_ms)
        drive=np.zeros(n,dtype=bool); mute=np.zeros(n,dtype=bool)
        for group in (stimulated,silenced):
            if any(type(i) is not int or not 0<=i<n for i in group): raise ValueError('Invalid index')
        drive[list(stimulated)]=True; mute[list(silenced)]=True; drive &= ~mute; driven=np.flatnonzero(drive)
        refr=np.full(n,round(p.refractory_ms/p.dt_ms),dtype=np.int32); refr[drive]=0
        v=np.full(n,p.rest_mv); g=np.zeros(n); next_active=np.zeros(n,dtype=np.int64)
        pending=np.zeros((delay+1,n)); counts=np.zeros(n,dtype=np.int64)
        weights=self.signed_counts*p.weight_mv
        weights[mute[self.pre]|mute[self.post]]=0
        if disconnected: weights.fill(0)
        rng=np.random.default_rng(seed)
        em=math.exp(-p.dt_ms/p.tau_mem_ms); es=math.exp(-p.dt_ms/p.tau_syn_ms)
        coupling=p.tau_syn_ms/(p.tau_syn_ms-p.tau_mem_ms)*(es-em)
        events=[]; start=time.perf_counter()
        for tick in range(steps):
            slot=tick%(delay+1); g+=pending[slot]; pending[slot].fill(0)
            active=(tick>=next_active)&~mute
            v[active]=p.rest_mv+(v[active]-p.rest_mv)*em+g[active]*coupling
            g[active]*=es
            t=(tick+1)*p.dt_ms
            if 200<=t<700 and len(driven):
                v[driven]+=rng.poisson(p.stimulus_hz*p.dt_ms/1000,size=len(driven))*p.stimulus_jump_mv
            spikes=(v>p.threshold_mv)&active
            if spikes.any():
                ix=np.flatnonzero(spikes); counts[ix]+=1
                events.extend((round(t,6),self.ids[i]) for i in ix)
                v[ix]=p.rest_mv; g[ix]=0; next_active[ix]=tick+1+refr[ix]
                used=spikes[self.pre]
                arrival=(tick+1+delay)%(delay+1)
                pending[arrival]+=np.bincount(self.post[used],weights=weights[used],minlength=n)
        arrays=[self.pre,self.post,self.signed_counts,v,g,pending,counts,next_active,weights,drive,mute,refr]
        return {'counts':counts.tolist(),'events':events,'wall_seconds':time.perf_counter()-start,
                'simulated_seconds':duration_ms/1000,'persistent_array_bytes':sum(a.nbytes for a in arrays),'parameters':asdict(p)}
