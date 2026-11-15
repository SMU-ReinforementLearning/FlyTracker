"""기존 기준선 설정을 읽어 신경 비행 시연 6개를 새로 기록한다.

기존 실행은 삭제하지 않는다. 원본 신경 코드·데이터와
기준선은 읽기만 하며 같은 이름의 보고서는 덮어쓰지 않는다.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

from flytracker import EnvConfig, EpisodeRecorder, FlyChaseEnv, NeuralConfig, RuleAimer, RunStore, StimulusConfig
from flytracker.free_flight import record_free_flight, record_tracking_observation

ROOT = Path(__file__).resolve().parents[1]
ISSUE = {'number': 31, 'title': '초파리 신경회로 연결 모델 추가',
         'url': 'https://github.com/SMU-ReinforementLearning/FlyTracker/issues/31'}


@dataclass(frozen=True)
class Demo:
    number: int
    name: str
    kind: str
    config: EnvConfig
    notes: str


def demo_specs(baseline, source):
    base = replace(EnvConfig.from_dict(baseline['env']), fly_model='neural')
    basic = replace(base, neural=NeuralConfig(source_root=str(source)), stimulus=StimulusConfig())
    no_stimulus = replace(basic, stimulus=replace(basic.stimulus, enabled=False))
    def free(cfg):
        return replace(cfg, max_seconds=30., capture_enabled=False,
                       stimulus=replace(cfg.stimulus, enabled=False))
    def observing(cfg):
        return replace(cfg, max_seconds=30., capture_enabled=False,
                       stimulus=replace(cfg.stimulus, max_events=100))
    return [
        Demo(1, '01 평시 비행 30초 (신경 날개 실험)', 'free-flight', free(basic),
             '신경 출력에서 날개 힘·토크를 적분하는 실험 모델이다. 실제 행동 일치는 미검증이다. 벽 감각으로 도피 phase가 발생할 수 있다.'),
        Demo(2, '02 평시 회로 대조 30초 (DNg02 억제)', 'free-flight',
             free(replace(basic, neural=replace(basic.neural, lesion='DNg02'))),
             '01과 같은 seed에서 DNg02를 억제한다. 날개 동역학에서는 날개 출력 소실과 추락·접촉을 확인하는 대조이며 자연 비행 시연이 아니다.'),
        Demo(3, '03 자극 반응 30초 (조준 반복)', 'tracking-observation', observing(basic),
             '4초 조준·4초 해제, 실제 정렬에 따른 가상 looming이다. 반응하지 않은 결과도 그대로 기록한다. 정답 기하 조준기는 시연용이다.'),
        Demo(4, '04 회로 대조 30초 (DNp06 억제)', 'tracking-observation',
             observing(replace(basic, neural=replace(basic.neural, lesion='DNp06'))),
             '03과 같은 seed와 조준 규칙에서 DNp06 출력을 억제한다. 확장 회로의 DNp03 반응은 남을 수 있으므로 전체 도피 억제 대조로 해석하지 않는다.'),
        Demo(5, '05 포획 종료 (신경 날개)', 'neural-tracking', basic,
             '기존 기준선의 seed·관측 기반 조준기·보상·포획 조건을 유지한다. 초파리에 신경 날개 모델을 사용한다.'),
        Demo(6, '06 포획 종료 (자극 없음)', 'neural-tracking', no_stimulus,
             '05와 같은 신경 날개 모델에서 가상 자극을 끈 대조다. 같은 seed라도 시선 연동 자극이 있으면 궤적이 달라질 수 있다.'),
    ]


def capture_episode(config, seed):
    # record_baseline.py와 같은 조준기 생성·reset·관측 기반 predict 순서다.
    policy = RuleAimer(max_pitch_deg=config.aimer.max_pitch_deg)
    recorder = EpisodeRecorder(FlyChaseEnv(config), meta={
        'policy': 'rule-baseline', 'mode': 'tracking-capture', 'captureEnabled': True,
        'aimerEnabled': True,
    })
    policy.reset()
    obs, _ = recorder.reset(seed=seed)
    done = False
    while not done:
        action, _ = policy.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = recorder.step(action)
        done = terminated or truncated
    return recorder.last_episode


def file_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def source_inventory(root):
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
            for part in ('flysim', 'data/stage2', 'output')
            for p in (root/part).rglob('*') if p.is_file()}


def verify_episode(ep, demo):
    f, meta = ep['frames'], ep['meta']
    n = len(f['t'])
    if meta['flyModel'] != 'neural' or meta['neural']['connections'] <= 0:
        raise ValueError('실제 신경회로 출처가 없는 기록')
    if any(len(values) != n for values in f.values()):
        raise ValueError('프레임 배열 길이 불일치')
    if not all(np.isfinite(f[k]).all() for k in ('t', 'fly', 'flyHeading', 'aimerC', 'aimerLook')):
        raise ValueError('비유한 비행 상태')
    for d in f['neuralDiagnostics']:
        if not np.isfinite([*d['velocity'], *d['quaternion'], *d['angular_velocity']]).all():
            raise ValueError('비유한 신경 모델 상태')
    diagnostic = ep['diagnostics']
    events = diagnostic['stimulus']['event_count']
    escape = sum(x['phase'] == 'escape' for x in diagnostic['phaseEvents'])
    sensory = max(max(x['left_input_hz'], x['right_input_hz']) for x in f['neuralDiagnostics'])
    output = max(max(x['dnp06_left_hz'], x['dnp06_right_hz']) for x in f['neuralDiagnostics'])
    if demo.kind != 'neural-tracking':
        if ep['summary']['duration'] != 30. or ep['summary']['captured']:
            raise ValueError('관찰 기록이 30초를 완료하지 못함')
        if demo.kind == 'free-flight' and (events or meta['aimerEnabled']):
            raise ValueError('무조준 비행에 가상 자극 또는 조준기가 있음')
        if demo.kind == 'tracking-observation':
            # A valid recording need not detect the stimulus or escape. Rejecting
            # nonresponses would select attractive examples instead of evidence.
            if demo.config.neural.lesion == 'DNp06' and output != 0:
                raise ValueError('DNp06 억제 대조에서 DNp06 출력이 남음')
    else:
        if not meta['captureEnabled'] or not demo.config.capture_enabled:
            raise ValueError('포획 종료 기록에서 포획이 꺼져 있음')
        if ep['summary']['captured'] and f['captureProgress'][-1] != 1.:
            raise ValueError('포획 완료 프레임 불일치')
    return dict(seed=meta['seed'], **ep['summary'], events=events, escapes=escape,
                max_sensory_hz=sensory, max_dnp06_hz=output,
                height_min=float(np.min(np.asarray(f['fly'])[:,1])),
                height_max=float(np.max(np.asarray(f['fly'])[:,1])),
                boundary_corrections=f['neuralDiagnostics'][-1]['boundary_corrections'])


def generate(source, runs, baseline, report):
    source, runs, baseline, report = (Path(p).resolve() for p in (source, runs, baseline, report))
    for destination in (runs, report):
        if destination == source or source in destination.parents:
            raise ValueError('원본 프로젝트 안에는 시연이나 보고서를 쓸 수 없다')
        if destination == baseline or baseline in destination.parents:
            raise ValueError('기준선 폴더를 시연 또는 보고서 출력 경로로 사용할 수 없다')
    if report.exists():
        raise FileExistsError('보고서가 이미 있다. 새 경로를 선택해 주세요.')
    baseline_before, source_before = file_hashes(baseline), source_inventory(source)
    config = json.loads((baseline/'config.json').read_text(encoding='utf-8'))
    manifest = json.loads((baseline/'episodes.json').read_text(encoding='utf-8'))
    seeds = [json.loads((baseline.parent/e['file']).read_text(encoding='utf-8'))['meta']['seed']
             for e in manifest['episodes']]
    if not seeds:
        raise ValueError('기준선의 에피소드 seed를 찾지 못함')
    result = dict(baseline_path=str(baseline), baseline_files_sha256=baseline_before,
                  source_path=str(source), source_files_checked=len(source_before),
                  new_runs=[])
    store = RunStore(runs)
    # viewer는 최신 실행부터 보인다. 역순 생성하여 01..06 순서로 표시한다.
    for demo in reversed(demo_specs(config, source)):
        captured = demo.kind == 'neural-tracking'
        tag = demo.kind
        run = store.create_run(demo.name, demo.kind, 'continuous' if demo.kind != 'free-flight' else 'none',
                               {'env': demo.config.to_dict(), 'mode': demo.kind,
                                'policy': 'rule-baseline' if captured else 'diagnostic',
                                'notes': demo.notes}, notes=demo.notes)
        store._update_run(run.id, issue=ISSUE)
        records = []
        for seed in (seeds if captured else [0]):
            if demo.kind == 'free-flight':
                ep = record_free_flight(demo.config, seed=seed)
            elif demo.kind == 'tracking-observation':
                ep = record_tracking_observation(demo.config, seed=seed, aim_on_seconds=4., aim_off_seconds=4.)
            else:
                ep = capture_episode(demo.config, seed)
            ep['meta']['demo'] = {'number': demo.number, 'name': demo.name, 'description': demo.notes}
            row = verify_episode(ep, demo)
            row['file'] = run.save_episode(ep, tag)
            records.append(row)
            print(f"{demo.name}: seed={seed}, {row['duration']:.2f}초, 포획={row['captured']}, 자극={row['events']}, 도피={row['escapes']}", flush=True)
        result['new_runs'].append(dict(id=run.id, name=demo.name, kind=demo.kind, tag=tag, episodes=records))
    result['baseline_unchanged'] = baseline_before == file_hashes(baseline)
    result['source_unchanged'] = source_before == source_inventory(source)
    if not result['baseline_unchanged'] or not result['source_unchanged']:
        raise RuntimeError('보존 대상 변경을 발견함')
    with report.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
    print(f'생성 보고서: {report}', flush=True)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--runs-dir', type=Path, default=ROOT/'runs')
    parser.add_argument('--baseline', type=Path, default=ROOT/'published/2026-11-11_133858_baseline')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    generate(args.source.resolve(), args.runs_dir.resolve(), args.baseline.resolve(), args.report.resolve())
