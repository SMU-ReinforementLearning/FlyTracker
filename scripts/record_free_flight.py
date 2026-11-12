"""포획 종료 없이 조준과 자극에 따른 비행을 기록한다.

--no-aim은 조준기와 가상 자극 없이 초파리 비행만 기록한다.
"""

import argparse
import sys
from uuid import uuid4

from flytracker import EnvConfig, NeuralConfig, RunStore, StimulusConfig
from flytracker.free_flight import record_free_flight, record_tracking_observation

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fly-model", choices=("rule", "neural"), default="neural")
    parser.add_argument("--neural-source", default=None)
    parser.add_argument("--neural-data", default=None)
    parser.add_argument("--seconds", type=float, default=30.)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--no-aim", action="store_true")
    parser.add_argument("--no-stimulus", action="store_true")
    parser.add_argument("--stimulus-max-events", type=int, default=100)
    parser.add_argument("--turret-pos", type=float, nargs=3, default=EnvConfig.turret_pos)
    parser.add_argument("--aim-on-seconds", type=float, default=4.)
    parser.add_argument("--aim-off-seconds", type=float, default=4.)
    parser.add_argument("--continuous-aim", action="store_true")
    parser.add_argument("--lesion", choices=("none", "LPLC2", "DNp06", "DNg02", "disconnected", "DNp03", "SGU", "escape"), default="none")
    args = parser.parse_args()
    if args.episodes <= 0:
        parser.error("episodes must be positive")
    cfg = EnvConfig(fly_model=args.fly_model, max_seconds=args.seconds,
                    neural=NeuralConfig(source_root=args.neural_source, data_dir=args.neural_data, lesion=args.lesion),
                    turret_pos=tuple(args.turret_pos),
                    stimulus=StimulusConfig(enabled=not (args.no_aim or args.no_stimulus),
                                            max_events=args.stimulus_max_events))
    mode = "free-flight" if args.no_aim else "tracking-observation"
    run = None
    for i in range(args.episodes):
        if args.no_aim:
            episode = record_free_flight(cfg, args.seed+i)
        else:
            episode = record_tracking_observation(cfg, args.seed+i,
                                                  None if args.continuous_aim else args.aim_on_seconds,
                                                  args.aim_off_seconds)
        if not args.no_save:
            if run is None:
                run = RunStore(args.runs_dir).create_run(
                    f"{mode}-{args.fly_model}-{args.lesion}-{uuid4().hex[:8]}", mode, "none" if args.no_aim else "continuous",
                    {"env": episode["meta"]["config"], "mode": mode})
            run.save_episode(episode, mode)
        print(f"{args.fly_model}: {episode['summary']['duration']:.2f}s, {episode['summary']['frames']} frames", flush=True)
    if run:
        print(f"Saved: {run.dir}")


if __name__ == "__main__":
    main()
