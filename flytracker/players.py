"""상대 자리에 넣는 player 와, 저장한 모델을 player 로 불러오는 함수.

player 는 reset() 과 act(관측) -> 행동 을 가진 객체다. 조준기 자리와 초파리 자리에 같은 모양으로 들어간다.
- 조준기 자리: "baseline"(기준선, 조준기 v0) 또는 학습한 조준기 모델
- 초파리 자리: "rule"(규칙 초파리, 초파리 v0) 또는 학습한 초파리 모델

모델은 실행 폴더(runs/<실행 id>, 그 안의 model.zip 을 쓴다)나 checkpoint 파일(runs/<실행 id>/checkpoints/<tag>.zip)로
가리킨다. 실행 폴더의 config.json 에서 환경 버전, 알고리즘, frame stack, 어느 쪽 모델인지를 읽는다.
환경 버전이 지금과 다르면 불러오지 않는다. 예외가 하나 있다. 환경 버전 5의 조준기 모델은 관측에 shot 이 없고
행동에 fire 가 없다는 것만 다르므로, 관측에서 shot 을 빼서 주고 쏠지는 기준선의 규칙(RuleAimer.wants_fire)으로 정해서 쓴다.
이렇게 불러온 모델은 조준만 학습한 것이고 쏘는 것은 배우지 않았다. Opponent.fire 가 "rule" 이다.
"""

from __future__ import annotations

import json
import warnings
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .baseline import RuleAimer
from .aimer import ACTION_DIM
from .env import ENV_VERSION, OBS, EnvConfig
from .wrappers import CONTROLS, DISCRETE_ACTIONS, FIRES, accel_gain, accel_to_rate

SIDES = ("aimer", "fly")
RULE_SPECS = {"aimer": "baseline", "fly": "rule"}
# 발사 행동이 생기기 전의 환경 버전. 이 버전의 조준기 모델은 쏘는 규칙을 붙여서 지금 환경에 넣을 수 있다
RULE_FIRE_VERSIONS = (5,)


def algo_classes() -> dict:
    """알고리즘 이름과 Stable-Baselines3 클래스. train extra 가 있어야 한다."""
    from stable_baselines3 import DQN, PPO, SAC, TD3

    return {"sac": SAC, "td3": TD3, "ppo": PPO, "dqn": DQN}


class PolicyPlayer:
    """predict(obs, deterministic=True) 를 가진 정책(SB3 모델, RuleAimer)을 player 로 감싼다.

    학습 때 frame stack 을 썼으면 최근 관측을 같은 방식으로 쌓는다. 에피소드 첫 관측으로 빈칸을 채운다
    (gymnasium FrameStackObservation 의 padding_type="reset" 과 같다). 이산 행동 모델이면 행동 번호를 연속 행동으로 바꾼다.
    """

    def __init__(self, policy, frame_stack: int = 1, discrete: bool = False, assist: float = 0.0, tracker: RuleAimer | None = None,
                 rule_fire: bool = False, accel_gain: np.ndarray | None = None):
        """assist 가 0 보다 크면 학습 때처럼 정책의 행동에 tracker 의 추적을 더한다 (wrappers.TrackingAssist).

        rule_fire 가 True 면 정책은 발사 행동이 없던 때(환경 버전 5)의 조준기 모델이다. 관측에서 shot 을 빼서 주고,
        정책이 낸 yaw, pitch 두 값에 tracker 의 쏘는 규칙으로 정한 fire 를 붙인다. 연속 행동 모델에만 쓴다.
        쏘는 것을 규칙에 맡겨 학습한 모델(실행의 algo.fire 가 "rule")도 같은 모양이다 (wrappers.RuleFire).

        accel_gain 을 주면 정책의 돌리는 행동은 각가속도다. 학습 때처럼 각속도 행동으로 바꿔서 쓴다 (wrappers.AccelControl).
        """
        if accel_gain is not None and discrete:
            raise ValueError("accel control needs a continuous-action policy")
        self.accel_gain = accel_gain
        if rule_fire and (discrete or tracker is None):
            raise ValueError("rule_fire needs a continuous-action policy and a tracker")
        self.rule_fire = rule_fire
        self.policy = policy
        self.frame_stack = frame_stack
        self.discrete = discrete
        self.assist = assist
        self.tracker = tracker
        self._stack: deque | None = None

    def reset(self) -> None:
        self._stack = None
        if hasattr(self.policy, "reset"):  # RuleAimer 는 탐색 상태를 에피소드마다 지운다
            self.policy.reset()

    def act(self, obs) -> np.ndarray:
        x = np.asarray(obs, dtype=np.float32)
        if self.rule_fire:
            x = np.delete(x, np.arange(len(x))[OBS["shot"]])
        if self.frame_stack > 1:
            if self._stack is None:
                self._stack = deque([x] * self.frame_stack, maxlen=self.frame_stack)
            else:
                self._stack.append(x)
            x = np.stack(self._stack)
        action, _ = self.policy.predict(x, deterministic=True)
        if self.discrete:
            return DISCRETE_ACTIONS[int(action)][1].copy()
        if self.rule_fire:
            action = np.append(np.asarray(action, dtype=float), np.zeros(ACTION_DIM - len(action)))
        if self.accel_gain is not None:
            action = accel_to_rate(obs, action, self.accel_gain)
        a = self.tracker.assisted(obs, action, self.assist) if self.assist > 0 else np.asarray(action, dtype=float)
        if self.rule_fire:
            a[2] = 1.0 if self.tracker.wants_fire(obs) else -1.0
        return a


@dataclass
class Opponent:
    player: PolicyPlayer | None  # 규칙 초파리는 None
    label: str  # 표와 config.json 에 적는 이름
    env_version: int  # 모델을 학습한 환경 버전
    fire: str = "policy"  # 쏠지를 누가 정하나. "policy" 는 정책, "rule" 은 기준선의 규칙 (환경 버전 5 모델)


def baseline_player(config: EnvConfig) -> PolicyPlayer:
    return PolicyPlayer(
        RuleAimer(
            max_pitch_deg=config.aimer.max_pitch_deg,
            max_yaw_rate_deg=config.aimer.max_yaw_rate_deg,
            max_pitch_rate_deg=config.aimer.max_pitch_rate_deg,
            fov_v_deg=config.camera.fov_v_deg,
            aspect=config.camera.aspect,
            fire_radius=config.capture_radius,
            fine_error_deg=config.fine_error_deg,
            room_diagonal=config.room.diagonal,
        )
    )


def load_opponent(spec: str, side: str, config: EnvConfig) -> Opponent:
    """spec 이 가리키는 side 쪽 player 를 만든다. side 는 "aimer" 또는 "fly"."""
    if side not in SIDES:
        raise ValueError(f"side 는 {SIDES} 중 하나다: {side!r}")
    if spec == RULE_SPECS[side]:
        player = baseline_player(config) if side == "aimer" else None
        return Opponent(player, spec, ENV_VERSION)
    if spec in RULE_SPECS.values():
        raise ValueError(f"{spec!r} 는 {side} 자리에 넣을 수 없다. {side} 자리의 규칙 상대는 {RULE_SPECS[side]!r} 다")

    model_path, run_dir = _resolve(spec)
    run_cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    version = run_cfg.get("envVersion", 1)
    algo = run_cfg.get("algo", {})
    control, fire = algo.get("control", "rate"), algo.get("fire", "policy")
    if control not in CONTROLS or fire not in FIRES:
        raise ValueError(f"{spec}: 알 수 없는 행동 방식이다 (control {control!r}, fire {fire!r})")
    old_rule_fire = side == "aimer" and version in RULE_FIRE_VERSIONS  # 발사 행동이 없던 때의 모델
    rule_fire = old_rule_fire or (side == "aimer" and fire == "rule")
    if version != ENV_VERSION and not old_rule_fire:
        raise ValueError(f"{spec}: 환경 버전 {version}에서 학습한 모델이라, 지금 환경(버전 {ENV_VERSION})과 견줄 수 없다")
    run_side = algo.get("side", "aimer")
    if run_side != side:
        raise ValueError(f"{spec}: {run_side} 쪽 모델이라 {side} 자리에 넣을 수 없다")
    if rule_fire and name_is_discrete(algo):
        raise ValueError(f"{spec}: 환경 버전 {version}의 이산 행동 모델에는 쏘는 규칙을 붙일 수 없다")
    if "env" in run_cfg:
        diff = _config_diff(EnvConfig.from_dict(run_cfg["env"]), config)
        if diff:
            warnings.warn(f"{spec}: 학습 때와 지금 환경 설정이 다르다: {', '.join(diff)}", stacklevel=2)
    name = algo.get("name")
    classes = algo_classes()
    if name not in classes:
        raise ValueError(f"{spec}: 알 수 없는 알고리즘 {name!r}")
    model = classes[name].load(model_path, device="cpu")
    assist = float(algo.get("assist", 0.0))
    player = PolicyPlayer(
        model,
        frame_stack=int(algo.get("frameStack", 1)),
        discrete=name == "dqn",
        assist=assist,
        tracker=baseline_player(config).policy if assist > 0 or rule_fire else None,
        rule_fire=rule_fire,
        accel_gain=accel_gain(config) if control == "accel" else None,
    )
    label = run_dir.name if model_path.name == "model.zip" else f"{run_dir.name}/{model_path.stem}"
    if rule_fire:
        label += "+rule-fire"  # 표에서 발사까지 학습한 모델과 구별한다
    return Opponent(player, label, version, fire="rule" if rule_fire else "policy")


def name_is_discrete(algo: dict) -> bool:
    return algo.get("name") == "dqn"


def _resolve(spec: str) -> tuple[Path, Path]:
    """spec 에서 모델 파일과 실행 폴더를 찾는다."""
    p = Path(spec)
    if p.is_dir():
        model, run_dir = p / "model.zip", p
    elif p.suffix == ".zip" and p.is_file():
        model = p
        run_dir = p.parent.parent if p.parent.name == "checkpoints" else p.parent
    else:
        raise FileNotFoundError(f"{spec}: 실행 폴더나 모델 파일(.zip)이 아니다")
    if not model.is_file():
        raise FileNotFoundError(f"{model} 가 없다")
    if not (run_dir / "config.json").is_file():
        raise FileNotFoundError(f"{run_dir / 'config.json'} 가 없다")
    return model, run_dir


def _config_diff(trained: EnvConfig, now: EnvConfig) -> list[str]:
    """두 설정에서 값이 다른 항목 이름. 보상 가중치는 상대로 쓸 때 상관없어서 뺀다."""
    a, b = trained.to_dict(), now.to_dict()
    return [k for k in a if k not in ("reward", "fly_reward") and a[k] != b.get(k)]
