"""보정 프로필과 실제 LIF 연결 배율을 사용하는 추가형 학습 환경."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
from .env import EnvConfig, FlyChaseEnv, ENV_VERSION
from .neural_fly import NeuralConfig

from .flight_profiles import PROFILE_ID, PROFILE, DATA_SHA256

def calibrated_config(**kwargs):
    return EnvConfig(fly_model="neural", neural=NeuralConfig(physics_overrides=PROFILE.copy(),
        profile_id=PROFILE_ID), **kwargs)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def contract(env):
    state = env.fly.sim.neural
    circuit = state.circuit
    material = hashlib.sha256()
    material.update(json.dumps(circuit.ids).encode())
    for x in (circuit.pre,circuit.post,circuit.signed_counts):
        material.update(x.tobytes())
    source = {n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()
              for n in ("neural_fly.py","neuromechanics.py","flight_network.py","flight_profiles.py","neural_training.py")}
    settings=env.config.to_dict()
    settings.pop("stimulus")  # Evaluation may turn the same stimulus off.
    return json.loads(json.dumps(dict(envVersion=ENV_VERSION, env=settings, sources=source,
                data=env.fly.backend.hashes, edgeOrder=material.hexdigest(),
                connections=len(state.weights))))

def groups(env):
    circuit=env.fly.sim.neural.circuit
    keys=[(circuit.nodes[int(i)]["cell_type"],circuit.nodes[int(i)]["side"],
           int(np.sign(w))) for i,w in zip(circuit.pre,circuit.signed_counts)]
    unique=sorted(set(keys))
    index={key:i for i,key in enumerate(unique)}
    return unique,np.array([index[key] for key in keys],dtype=np.int64)

class GroupedWeights:
    """동일 presynaptic cell type, side, sign의 연결이 하나의 양의 배율을 공유한다."""
    def __init__(self, signature, keys, theta):
        self.signature=signature
        self.keys=[tuple(k) for k in keys]
        self.theta=np.asarray(theta,dtype=np.float64).copy()
        if (self.theta.shape!=(len(keys),) or not np.isfinite(self.theta).all()
                or np.any(np.abs(self.theta)>np.log(2)+1e-12)):
            raise ValueError("Invalid grouped weights")
    @classmethod
    def identity(cls,env):
        keys,_=groups(env)
        return cls(contract(env),keys,np.zeros(len(keys)))
    def updated(self,theta):
        return type(self)(self.signature,self.keys,np.clip(theta,-np.log(2),np.log(2)))
    @property
    def sha256(self):
        return digest(dict(signature=self.signature,keys=self.keys,theta=self.theta.tolist()))
    def apply(self,env):
        state=env.fly.sim.neural
        if state.tick!=0 or getattr(state,"_grouped_weights_applied",False) or contract(env)!=self.signature:
            raise ValueError("Weights require the same circuit/config and a freshly reset state")
        keys,index=groups(env)
        if keys!=self.keys:
            raise ValueError("Weight group order changed")
        state.weights*=np.exp(self.theta[index])
        state._grouped_weights_applied=True
    def save(self,path,metadata=None):
        with Path(path).open("xb") as stream:
            np.savez_compressed(stream,theta=self.theta,
                manifest=np.array(json.dumps(dict(format="grouped-lif-weights/1",
                    signature=self.signature,keys=self.keys,sha256=self.sha256,
                    metadata=metadata or {}))))
    @classmethod
    def load(cls,path):
        with np.load(path,allow_pickle=False) as data:
            meta=json.loads(str(data["manifest"].item()))
            if meta["format"]!="grouped-lif-weights/1":
                raise ValueError("Unsupported format")
            result=cls(meta["signature"],meta["keys"],data["theta"])
        if result.sha256!=meta["sha256"]:
            raise ValueError("Weight checksum mismatch")
        return result

class WeightedEnv(FlyChaseEnv):
    def __init__(self,config,weights=None):
        if config.fly_model!="neural" or config.neural.lesion!="none":
            raise ValueError("An intact neural fly is required")
        self.weights=weights
        super().__init__(config)
    def reset(self,**kwargs):
        obs,info=super().reset(**kwargs)
        if self.weights is not None:
            self.weights.apply(self)
            info["groupedWeightsSha256"]=self.weights.sha256
        return obs,info
    def recording_metadata(self):
        result=super().recording_metadata()
        if self.weights is not None:
            result["neural"]["learned_weights"]=dict(sha256=self.weights.sha256,
                parameterization="presynaptic cell type/side/sign shared positive gain",
                groups=len(self.weights.theta),gain_range=[0.5,2.])
        return result
