"""Read a user-selected local Muijres Database S1 ZIP; export derived metrics only.

External raw data must stay outside this repository. Requires scipy only for
this offline research command; it is not a FlyTracker runtime dependency.
Reference species/protocol differ from the installed connectome model: these
descriptive values are not a calibration score or a reproduction of Fig. 2.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np


def summarize_reference(data):
    body, settings = data['body_data'], data['settings_variables']
    t = np.asarray(body['t'], dtype=float)
    q, velocity, accel = (np.asarray(body[k], dtype=float) for k in ('qbody', 'vel', 'accel'))
    if t.ndim != 1 or not np.all(np.isfinite(t)) or not np.all(np.diff(t) > 0):
        raise ValueError('Expected strictly increasing finite reference seconds')
    if velocity.shape != accel.shape or velocity.shape != (len(t), len(settings['seq']), 3):
        raise ValueError('Unexpected reference vector dimensions')
    if q.shape != (*velocity.shape[:2], 4):
        raise ValueError('Unexpected reference quaternion dimensions')
    # Quaternion distance is invariant to scalar component position, sign and
    # world/body inversion; it gives angular SPEED without guessing body axes.
    qnorm = np.linalg.norm(q, axis=2)
    norm_error = abs(qnorm-1)
    if np.any(np.isfinite(qnorm) & ((qnorm == 0) | (norm_error > .01))):
        raise ValueError('Reference quaternion norm differs from one by more than 1%')
    q = q / qnorm[..., None]
    dots = np.sum(q[1:]*q[:-1], axis=2)
    angular = 2*np.arccos(np.clip(abs(dots), 0, 1))/np.diff(t)[:, None]
    speed = np.linalg.norm(velocity, axis=2)
    acceleration = np.linalg.norm(accel, axis=2)
    position = np.asarray(body['pos'], dtype=float)
    finite_difference = (position[2:]-position[:-2])/(t[2:]-t[:-2])[:, None, None]
    relative_error = np.linalg.norm(finite_difference-velocity[1:-1], axis=2)/np.maximum(speed[1:-1], 1e-4)
    derivative_error = float(np.median(relative_error[np.isfinite(relative_error)]))
    expansion = settings['expansion']
    theta = np.asarray(data['stimulus_data']['teta'])
    rows = []
    for i, sequence in enumerate(settings['seq']):
        mask = np.isfinite(speed[:, i])
        if not mask.any():
            raise ValueError(f'Sequence {i} has no finite velocity')
        after = (t >= 0) & np.isfinite(acceleration[:, i])
        crossings = np.flatnonzero(after & (acceleration[:, i] >= .28*settings['g']))
        angular_values = angular[(t[1:] >= 0) & np.isfinite(angular[:, i]), i]
        pre = (t < 0) & mask
        positive = t[mask & (theta[:, i] > 0)]
        rows.append(dict(sequence=f'{sequence[0]}-{sequence[1]}', speed_code=int(expansion['speed'][i]),
                         finite_velocity_samples=int(mask.sum()),
                         first_positive_stimulus_time_s=float(positive[0]) if len(positive) else None,
                         pre_speed_median=float(np.median(speed[pre, i])) if pre.any() else None,
                         speed_max=float(speed[mask, i].max()),
                         angular_speed_max_rad_s=float(angular_values.max()) if len(angular_values) else None,
                         acceleration_crossing_after_trigger_ms=float(t[crossings[0]]*1000) if len(crossings) else None,
                         already_above_threshold_at_first_posttrigger_sample=bool(
                             len(crossings) and crossings[0] == np.flatnonzero(after)[0])))
    def distribution(values):
        a = np.array([v for v in values if v is not None])
        if not len(a):
            return dict(n=0, min=None, median=None, max=None)
        return dict(n=len(a), min=float(a.min()), median=float(np.median(a)), max=float(a.max()))
    return dict(reference='Muijres et al. 2014 Database S1', species='Drosophila hydei',
                scope='Descriptive selected maneuver records, not independent flies or a matched biological validation',
                fps=int(settings['fps']), sequences=len(rows), g=float(settings['g']),
                raw_quaternion_norm_max_error=float(np.nanmax(norm_error)),
                raw_quaternions_over_1e3_error=int(np.sum(norm_error > 1e-3)),
                quaternion_preprocessing='Normalize finite positive quaternions; reject norm error >1%; record original errors',
                body_length_m=float(settings['Lbody']), mass_kg=float(settings['Mfly']),
                position_velocity_derivative_relative_error_median=derivative_error,
                kinematic_unit_consistency=derivative_error < .1,
                raw_fields=['body_data.t', 'body_data.vel', 'body_data.accel', 'body_data.qbody', 'stimulus_data.teta'],
                angle_method='2*acos(abs(dot(normalized q(t),q(t+dt))))/dt; no Euler-axis convention assumed',
                threshold_note='First finite post-trigger crossing of |a|>=0.28*g, not an independently reconstructed published response onset',
                speed_units_note='SI metadata g=9.81, Lbody in metres; no invented scaling; velocity/position derivative consistency is checked separately',
                pre_speed_median_distribution=distribution([r['pre_speed_median'] for r in rows]),
                peak_speed_distribution=distribution([r['speed_max'] for r in rows]),
                peak_angular_speed_distribution=distribution([r['angular_speed_max_rad_s'] for r in rows]),
                sequences_by_speed_code={str(c):sum(r['speed_code']==c for r in rows) for c in (0,1,2)},
                already_above_threshold=sum(r['already_above_threshold_at_first_posttrigger_sample'] for r in rows))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if root == args.zip.resolve() or root in args.zip.resolve().parents:
        parser.error('External reference ZIP must stay outside the repository')
    if args.output.exists():
        parser.error('Output exists; choose a new derived result file')
    import scipy
    from scipy.io import loadmat
    raw = args.zip.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        payload = archive.read('FRUITFLY_LOOMINGRESPONSE_DATABASE.mat')
    data = loadmat(io.BytesIO(payload), simplify_cells=True)
    result = summarize_reference(data)
    result.update(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                  source_url='https://authors.library.caltech.edu/records/fgsdt-n4t54',
                  raw_zip_sha256=hashlib.sha256(raw).hexdigest(), raw_mat_sha256=hashlib.sha256(payload).hexdigest(),
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  rights='Repository metadata grants no commercial reproduction/distribution/display/performance rights; raw material not bundled')
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))
