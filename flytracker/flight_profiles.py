"""공개 실측 보정 후보의 고정 프로필. 통계적 채택과 사용자 선택 적용을 구분한다."""
from __future__ import annotations
import hashlib
import json

PROFILE_ID = "zenodo29193-candidate13-experimental"
ORIGINAL_PROFILE_ID = "original"
PROFILE = {
    "drag_coefficient": 0.6965822171013261,
    "stroke_plane_forward_rad": 0.16524623644691436,
    "saccade_rotation_gain_rad": 0.08406764548975353,
    "background_drive_hz": 1.0077175328589492,
}
DATA_SHA256 = "8167a67b8241772daf3f117e8b6faca69f2a9e130918558d47f2cb4f07846e0d"

def profile_parameters(profile_id):
    if profile_id == PROFILE_ID:
        return PROFILE.copy()
    if profile_id in (None, ORIGINAL_PROFILE_ID):
        return {}
    raise ValueError("Unknown neural flight profile: " + str(profile_id))

def profile_provenance(profile_id, physics):
    payload=json.dumps(physics,sort_keys=True,separators=(",",":")).encode()
    result=dict(id=profile_id,physics_sha256=hashlib.sha256(payload).hexdigest())
    if profile_id == PROFILE_ID:
        result.update(source="https://zenodo.org/records/29193",data_sha256=DATA_SHA256,
            condition="4-day female GFP genetic controls, gray visual condition, 3-second snippets",
            preregistered_gate_passed=False,bootstrap_probability=.879,
            adoption_threshold=.90,status="experimental user-selected calibration")
    else:
        result["status"]="original or explicitly customized mechanics"
    return result
