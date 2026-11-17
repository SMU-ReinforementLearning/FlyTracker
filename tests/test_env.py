from dataclasses import replace

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from flytracker import OBS, OBS_DIM, EnvConfig, FlyChaseEnv, make_env
from flytracker.fly import FlyParams


def test_env_passes_gymnasium_checker():
    check_env(FlyChaseEnv(), skip_render_check=True)


def test_discrete_actions_drive_one_axis():
    env = make_env(action_mode="discrete")
    env.reset(seed=0)
    assert env.action_space.n == 6
    for a in range(env.action_space.n):
        obs, *_ = env.step(a)
        assert env.observation_space.contains(obs)


def test_same_seed_same_episode():
    def rollout():
        env = FlyChaseEnv(EnvConfig())
        obs, _ = env.reset(seed=123)
        rng = np.random.default_rng(0)
        seq = [obs]
        for _ in range(100):
            obs, *_ = env.step(rng.uniform(-1, 1, 3))
            seq.append(obs)
        return np.array(seq)

    assert np.array_equal(rollout(), rollout())


def static_fly_config(**kw) -> EnvConfig:
    fly = FlyParams.hovering()
    return replace(EnvConfig(fly=fly), **kw)


FIRE = np.array([0.0, 0.0, 1.0])  # 돌리지 않고 쏜다


def test_holding_fly_in_center_captures():
    cfg = static_fly_config()
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + env.aimer.look * 0.3  # 바로 앞 0.3m 에 둔다
    env._update_vision()
    total, steps, terminated = 0.0, 0, False
    while not terminated and steps < 100:
        _, r, terminated, truncated, info = env.step(FIRE)
        total += r
        steps += 1
    assert terminated and info["captured"]
    expected_steps = round(cfg.capture_hold / (cfg.dt * cfg.frame_skip))
    assert steps == pytest.approx(expected_steps, abs=1)
    assert total > cfg.reward.capture - 1.0


def test_time_limit_truncates():
    env = FlyChaseEnv(replace(EnvConfig(), max_seconds=0.1))
    env.reset(seed=0)
    truncated = False
    for _ in range(5):
        _, _, terminated, truncated, _ = env.step(np.zeros(3))
    assert truncated and not terminated


def test_frame_stack_shape():
    env = make_env(frame_stack=4)
    obs, _ = env.reset(seed=0)
    assert obs.shape == (4, OBS_DIM)


def test_observation_hides_fly_when_out_of_view():
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos - env.aimer.look * 1.0  # 바로 뒤
    env._update_vision()
    obs = env._observation()
    assert obs[OBS["visible"]][0] == 0.0
    assert np.all(obs[OBS["uv"]] == 0.0)


def test_turret_stays_at_configured_position():
    cfg = replace(EnvConfig(), turret_pos=(1.0, 0.8, -1.0))
    env = FlyChaseEnv(cfg)
    env.reset(seed=3)
    rng = np.random.default_rng(1)
    for _ in range(50):
        env.step(rng.uniform(-1, 1, 3))
        assert np.array_equal(env.aimer.pos, np.array(cfg.turret_pos))


def test_turret_outside_room_is_rejected():
    with pytest.raises(ValueError):
        FlyChaseEnv(replace(EnvConfig(), turret_pos=(0.0, 1.0, 5.0)))


def test_capture_range_none_captures_far_fly():
    cfg = static_fly_config()
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + env.aimer.look * 2.5  # 2.5m 앞. 거리 조건이 없으면 잡힌다
    env._update_vision()
    terminated, steps = False, 0
    while not terminated and steps < 100:
        _, _, terminated, _, info = env.step(FIRE)
        steps += 1
    assert info["captured"]


def test_fly_straight_above_turret_is_captured():
    # pitch 가 90° 까지 돌아서 바로 위에도 빔이 닿는다.
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + np.array([0.0, 1.9, 0.0])  # 바로 위 1.9m. 위협 반경(1m) 밖이라 피하지 않는다
    env._update_vision()
    info = {"captured": False}
    for _ in range(150):  # 3초 동안 위로 돌린다
        obs, _, terminated, _, info = env.step(np.array([0.0, 1.0, 1.0]))
        if terminated:
            break
    assert info["captured"] is True
    assert env.aimer.pitch == pytest.approx(np.pi / 2)
    assert info["beam_dist"] < 1e-9


def test_camera_frame_is_continuous_through_straight_up():
    # 바로 위를 볼 때도 화면 좌표가 끊기지 않는다. 89.9° 와 90° 에서 같은 점의 화면 좌표가 0.1° 만큼만 다르다.
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    yaw = 0.7
    point = env.aimer.pos + np.array([0.05, 2.0, -0.03])  # 바로 위에서 조금 벗어난 점
    env.fly.pos = point
    uvs = []
    for pitch_deg in (89.9, 90.0):
        env.aimer.reset(env.aimer.pos, yaw, np.radians(pitch_deg))
        env._update_vision()
        assert env._proj.visible
        uvs.append(env._proj.uv.copy())
    step = np.tan(np.radians(0.1)) / env.config.camera.tan_half_v  # pitch 0.1° 가 세로 화면 좌표에서 차지하는 크기
    assert uvs[1][0] == pytest.approx(uvs[0][0], abs=1e-4)
    assert uvs[0][1] - uvs[1][1] == pytest.approx(step, rel=0.01)
    r, u, f = env.aimer.basis
    assert np.allclose(f, [0, 1, 0]) and np.allclose(r, [np.cos(yaw), 0, -np.sin(yaw)])
    assert np.allclose(u, [np.sin(yaw), 0, np.cos(yaw)])  # 화면 위쪽은 수평 앞 방향의 반대쪽


def test_observation_has_target_rate_and_fine_error():
    cfg = static_fly_config()
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    # 2m 앞, 빔에서 오른쪽으로 7mm (0.2°). uv_fine 은 0.2° / 0.5° = 0.4 이고, uv 로는 0.007 이다.
    r, _, f = env.aimer.basis
    off = 2.0 * np.tan(np.radians(0.2))
    env.fly.pos = env.aimer.pos + f * 2.0 + r * off
    env._target_angles = None
    env._update_vision()
    obs = env._observation()
    assert obs[OBS["uv_fine"]] == pytest.approx([0.4, 0.0], abs=1e-4)
    assert abs(obs[OBS["uv"]][0]) < 0.01
    assert obs[OBS["target_rate"]] == pytest.approx([0.0, 0.0])
    # 초파리를 물리 step 하나(0.01초)에 오른쪽으로 0.09° 옮긴다. 9°/s 이고 yaw 는 줄어든다(오른쪽). 최대 180°/s 의 −0.05.
    env.fly.pos = env.aimer.pos + f * 2.0 + r * 2.0 * np.tan(np.radians(0.29))
    env._update_vision()
    obs = env._observation()
    assert obs[OBS["target_rate"]] == pytest.approx([-0.05, 0.0], abs=1e-4)
    # 안 보이면 둘 다 0 이다.
    env.fly.pos = env.aimer.pos - f * 2.0
    env._update_vision()
    obs = env._observation()
    assert not obs[OBS["target_rate"]].any() and not obs[OBS["uv_fine"]].any()


def test_rule_aimer_holds_the_beam_on_a_moving_fly():
    # 기준선은 초파리 각속도에 맞춰 돌아서 기본 초파리를 레이저 명중 조건으로 잡는다.
    from flytracker import RuleAimer

    env, policy, caught = FlyChaseEnv(EnvConfig()), RuleAimer(), 0
    for seed in range(5):
        obs, info = env.reset(seed=seed)
        policy.reset()
        done = False
        while not done:
            obs, _, terminated, truncated, info = env.step(policy.act(obs))
            done = terminated or truncated
        caught += info["captured"]
    assert caught >= 4


def _held_fly_env(offset_m: float = 0.0, distance: float = 2.0, **kw) -> FlyChaseEnv:
    """가만히 있는 초파리를 조준 방향에서 옆으로 offset_m 만큼 떨어뜨려 둔다."""
    env = FlyChaseEnv(static_fly_config(**kw))
    env.reset(seed=0)
    side = np.cross(env.aimer.look, np.array([0.0, 1.0, 0.0]))
    env.fly.pos = env.aimer.pos + env.aimer.look * distance + side / np.linalg.norm(side) * offset_m
    env._update_vision()
    return env


def test_capture_needs_fifteen_physics_steps_on_the_beam():
    env = _held_fly_env()
    assert env.config.capture_hold == pytest.approx(0.15) and env.config.dt == 0.01
    for _ in range(7):  # 물리 step 14번
        _, _, terminated, _, info = env.step(FIRE)
        assert not terminated and not info["captured"]
    _, _, terminated, _, info = env.step(FIRE)  # 15번째에서 잡힌다
    assert terminated and info["captured"]
    assert info["t"] == pytest.approx(0.15)
    assert (info["shots"], info["misfires"]) == (1, 0)


def test_no_capture_without_firing():
    # 빔이 초파리 위에 있어도 쏘지 않으면 잡히지 않는다.
    env = _held_fly_env()
    for _ in range(20):
        obs, _, terminated, _, info = env.step(np.zeros(3))
        assert not terminated and obs[OBS["shot"]][0] == 0.0
    assert info["beam_dist"] == pytest.approx(0.0, abs=1e-9)
    assert (info["shots"], info["misfires"], info["firing"]) == (0, 0, False)


def test_shot_cannot_be_stopped_and_observation_counts_it_down():
    # 한 번 쏘면 0.15초 동안 이어진다. 그동안 관측 shot 이 1 에서 0 으로 줄고, 다시 당긴 방아쇠는 무시된다.
    env = _held_fly_env(offset_m=0.01)  # 빔에서 1cm 떨어져 있어 맞지 않는다
    obs, _, _, _, info = env.step(FIRE)
    assert info["firing"] and (info["shots"], info["misfires"]) == (1, 1)
    assert obs[OBS["shot"]][0] == pytest.approx(13 / 15)
    for left in (11, 9, 7, 5, 3, 1):  # 쏘지 않아도, 또 쏘아도 같은 한 발이 이어진다
        obs, _, _, _, info = env.step(FIRE if left % 4 == 1 else np.zeros(3))
        assert obs[OBS["shot"]][0] == pytest.approx(left / 15) and info["shots"] == 1
    obs, _, _, _, info = env.step(np.zeros(3))  # 한 발이 끝난다
    assert obs[OBS["shot"]][0] == 0.0 and info["firing"]
    obs, _, _, _, info = env.step(np.zeros(3))
    assert not info["firing"] and (info["shots"], info["misfires"]) == (1, 1)


@pytest.mark.parametrize("offset_mm, captured", [(1.2, True), (1.3, False), (52.0, False)])
def test_capture_is_decided_by_distance_to_the_beam(offset_mm, captured):
    # 52mm 는 1m 에서 3° 다. 이전 조건(3°)으로는 잡히던 자리다.
    env = _held_fly_env(offset_m=offset_mm / 1000, distance=1.0)
    info = {}
    for _ in range(20):
        _, _, terminated, _, info = env.step(FIRE)
        if terminated:
            break
    assert info["captured"] is captured
    assert info["beam_dist"] * 1000 == pytest.approx(offset_mm, abs=1e-6)
    assert info["misfires"] == (0 if captured else info["shots"])  # 빗나간 자리에서 쏜 발은 모두 오발이다


def test_shot_that_leaves_the_fly_is_a_misfire_and_the_next_shot_can_capture():
    env = _held_fly_env()
    for _ in range(6):
        env.step(FIRE)
    on_beam = env.fly.pos.copy()
    env.fly.pos = on_beam + np.array([0.0, 0.01, 0.0])  # 빔에서 1cm 벗어난다
    _, _, terminated, _, info = env.step(FIRE)
    assert not terminated and (info["shots"], info["misfires"]) == (1, 1)
    assert env.snapshot()["captureProgress"] == 0.0
    env.fly.pos = on_beam
    _, _, terminated, _, info = env.step(FIRE)  # 빗나간 발의 마지막 물리 step. 다시 맞아도 이 발은 오발이다
    assert not terminated and info["shots"] == 1
    for _ in range(7):
        _, _, terminated, _, info = env.step(FIRE)
        assert not terminated and info["shots"] == 2
    _, _, terminated, _, info = env.step(FIRE)
    assert terminated and info["captured"] and (info["shots"], info["misfires"]) == (2, 1)


def test_fly_behind_the_turret_is_not_hit():
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos - env.aimer.look * 0.5  # 빔의 연장선 위지만 조준기 뒤다
    env._update_vision()
    assert env._info()["beam_dist"] == pytest.approx(0.5)
    for _ in range(20):
        _, _, terminated, _, info = env.step(FIRE)
    assert not info["captured"]
