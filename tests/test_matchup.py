import numpy as np
import pytest

from flytracker import ENV_VERSION, EnvConfig, EpisodeRecorder, Opponent, RuleAimer, load_opponent, make_env
from flytracker.matchup import format_table, play_cell, play_table


class EscapingFly:
    """step 마다 왼쪽으로 크게 빠르게 피하는 초파리."""

    def reset(self):
        pass

    def act(self, obs):
        return np.array([1.0, 0.5, 0.0, 1.0])


def test_baseline_vs_rule_cell_matches_recorded_baseline_episodes():
    cfg = EnvConfig()
    seeds = range(3, 8)
    cell = play_cell(cfg, load_opponent("baseline", "aimer", cfg), load_opponent("rule", "fly", cfg), seeds)

    env, policy, captured, times = EpisodeRecorder(make_env(cfg)), RuleAimer(), 0, []
    for seed in seeds:
        policy.reset()
        obs, _ = env.reset(seed=seed)
        done = False
        while not done:
            obs, _, terminated, truncated, _ = env.step(policy.act(obs))
            done = terminated or truncated
        if env.last_episode["summary"]["captured"]:
            captured += 1
            times.append(env.last_episode["summary"]["duration"])
    assert cell.captured == captured
    assert cell.capture_times == pytest.approx(times)


def test_table_has_a_row_per_aimer_and_a_column_per_fly():
    cfg = EnvConfig()
    aimers = [load_opponent("baseline", "aimer", cfg)]
    flies = [load_opponent("rule", "fly", cfg), Opponent(EscapingFly(), "escaping", ENV_VERSION)]
    cells = play_table(cfg, aimers, flies, range(2))
    assert len(cells) == 1 and len(cells[0]) == 2
    text = format_table(aimers, flies, cells)
    assert text.splitlines()[0] == "| 조준기 \\ 초파리 | rule | escaping |"
    assert text.splitlines()[2].startswith("| baseline | ")
    assert all(c.episodes == 2 for c in cells[0])
