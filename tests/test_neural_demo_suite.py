"""시연을 위해 기존 포획 규칙이나 기준선 데이터를 바꾸지 않는다."""
from dataclasses import replace
import json
from pathlib import Path

import pytest

from scripts.record_neural_demo_suite import demo_specs, generate


def test_capture_demos_keep_published_baseline_contract():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'published/2026-11-11_133858_baseline/config.json').read_text(encoding='utf-8'))
    original = json.loads(json.dumps(data))
    specs = demo_specs(data, 'local-source')
    assert len(specs) == 6 and data == original
    base = specs[4].config
    for spec in specs[4:]:
        cfg = spec.config
        assert cfg.capture_enabled and cfg.capture_angle_deg == 3. and cfg.capture_hold == .2
        assert cfg.max_seconds == 10. and not cfg.start_facing_fly
        assert replace(cfg, neural=base.neural, stimulus=base.stimulus) == base
    for spec in specs[:4]:
        assert spec.config.max_seconds == 30. and not spec.config.capture_enabled
    assert not specs[0].config.stimulus.enabled and not specs[1].config.stimulus.enabled
    assert specs[3].config.neural.lesion == 'DNp06'




@pytest.mark.parametrize('protected', ['source', 'baseline'])
@pytest.mark.parametrize('destination', ['runs', 'report'])
def test_demo_outputs_reject_protected_directories_before_reading_or_writing(tmp_path, protected, destination):
    source, baseline = tmp_path/'source', tmp_path/'baseline'
    runs, report = tmp_path/'runs', tmp_path/'report.json'
    target = source if protected == 'source' else baseline
    # Resolve parent segments even when the Python API is used without the CLI.
    unsafe = target/'nested'/'..'/'new-output'
    if destination == 'runs':
        runs = unsafe
    else:
        report = unsafe
    with pytest.raises(ValueError):
        generate(source, runs, baseline, report)
    assert list(tmp_path.iterdir()) == []
