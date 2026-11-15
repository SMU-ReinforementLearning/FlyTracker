"""The already axis-converted fly mesh must preserve recorded body roll."""
import json
import math
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest


def multiply(a, b):
    w, x, y, z = a; v, i, j, k = b
    return np.array([w*v-x*i-y*j-z*k, w*i+x*v+y*k-z*j, w*j-x*k+y*v+z*i, w*k+x*j-y*i+z*v])


def rotate(q, v):
    return multiply(multiply(q, [0, *v]), q * [1, -1, -1, -1])[1:]


def episode(qs):
    n = len(qs)
    return dict(meta={}, summary={}, frames=dict(
        t=[.02*i for i in range(n)], reward=[0]*n, fly=[[0, 1, 0]]*n,
        flyHeading=[rotate(np.array(q), [1, 0, 0]).tolist() for q in qs],
        aimerC=[[0, 0, 0]]*n, aimerLook=[[0, 0, -1]]*n, uv=[[0, 0]]*n,
        visible=[False]*n, alarmed=[False]*n, captureProgress=[0]*n,
        angleErrDeg=[0]*n, distance=[1]*n,
        neuralDiagnostics=[dict(quaternion=list(q), normal_rate_hz=0, dnp06_left_hz=0,
                                dnp06_right_hz=0, left_input_hz=0, right_input_hz=0) for q in qs]))


def test_actual_mesh_axes_and_shortest_arc_interpolation_preserve_attitude():
    if not shutil.which('node'):
        pytest.skip('Node is required for actual viewer loader')
    root = Path(__file__).resolve().parents[1]
    amap = np.array([.5, -.5, .5, .5])
    rows = []
    for axis in ([1, 0, 0], [0, 1, 0], [0, 0, 1]):
        for angle in (0, math.pi/3, -math.pi/2, math.pi):
            native = np.array([math.cos(angle/2), *(np.array(axis)*math.sin(angle/2))])
            world = multiply(amap, native)
            rows.append(dict(ep=episode([world, -world]), forward=rotate(world, [1, 0, 0]).tolist(),
                             up=rotate(world, [0, 0, 1]).tolist()))
    start = amap
    end = multiply(amap, [math.sqrt(.5), math.sqrt(.5), 0, 0])
    middle = multiply(amap, [math.cos(math.pi/8), math.sin(math.pi/8), 0, 0])
    rows.append(dict(ep=episode([start, end]), forward=rotate(middle, [1, 0, 0]).tolist(), up=rotate(middle, [0, 0, 1]).tolist()))
    loader = (root/'viewer/src/data/episode.js').as_uri()
    three = (root/'viewer/node_modules/three/build/three.module.js').as_uri()
    code = f"""
import {{prepareEpisode,sample,newSample}} from {json.dumps(loader)};
import {{Quaternion,Vector3}} from {json.dumps(three)};
let input='';for await(const c of process.stdin)input+=c;
const rows=JSON.parse(input);
for(const row of rows){{
 const ep=prepareEpisode(row.ep), s=sample(ep,.01,newSample());
 const q=new Quaternion(...s.meshQuaternion);
 for(const [axis,expected] of [[[0,0,-1],row.forward],[[0,1,0],row.up]]){{
  if(new Vector3(...axis).applyQuaternion(q).distanceTo(new Vector3(...expected))>1e-12)throw Error('mesh-axis mismatch');
 }}
 if(!s.hasAttitude)throw Error('attitude missing');
}}
const legacy=structuredClone(rows[0].ep);delete legacy.frames.neuralDiagnostics;
if(sample(prepareEpisode(legacy),.01,newSample()).hasAttitude)throw Error('legacy fallback');
const invalid=structuredClone(rows[0].ep);invalid.frames.neuralDiagnostics[0].quaternion=[0,0,0,0];
let rejected=false;try{{prepareEpisode(invalid)}}catch{{rejected=true}}if(!rejected)throw Error('invalid attitude accepted');
"""
    subprocess.run(['node', '--input-type=module', '-e', code], input=json.dumps(rows), text=True, check=True, capture_output=True)


def test_extended_rates_include_dnp03_and_keep_wall_input_separate():
    if not shutil.which('node'):
        pytest.skip('Node is required for actual viewer loader')
    ep=episode([[1,0,0,0]])
    ep['frames']['neuralDiagnostics'][0].update(
        extended_rates=dict(dnp03_left_hz=120,dnp03_right_hz=5,sgu_left_hz=18,sgu_right_hz=0),
        wall_sensory=dict(left=45,right=10))
    loader=(Path(__file__).resolve().parents[1]/'viewer/src/data/episode.js').as_uri()
    code=f"""
import {{prepareEpisode}} from {json.dumps(loader)};
let input='';for await(const c of process.stdin)input+=c;
const raw=JSON.parse(input), ep=prepareEpisode(raw);
if(ep.escapeRate[0]!==120||ep.saccadeRate[0]!==18||ep.wallInput[0]!==45||ep.threatInput[0]!==0)throw Error('extended rate mismatch');
delete raw.frames.neuralDiagnostics[0].extended_rates;delete raw.frames.neuralDiagnostics[0].wall_sensory;
const old=prepareEpisode(raw);if(old.escapeRate[0]!==0||old.saccadeRate!==null||old.wallInput!==null)throw Error('legacy rates');
"""
    subprocess.run(['node','--input-type=module','-e',code],input=json.dumps(ep),text=True,check=True,capture_output=True)
