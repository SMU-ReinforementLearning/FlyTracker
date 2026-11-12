# UI evidence — neural

- Generated: 2026-11-12T13:57:03.420Z
- Base: `http://127.0.0.1:5181`
- Pages: `http://127.0.0.1:5181/?run=2026-11-12_180710_02-30&tag=tracking-observation&ep=1`
- Commit: 7237428 (dirty)
- Chrome: Chrome/157.0.8103.40 (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- Viewports: 1600x900, 390x844 (mobile, dpr 2)
- Ready: `document.querySelector('.readouts') !== null && document.querySelector('canvas') !== null` · settle 800 ms · reduced-motion on · per-shot timeout 45000 ms
- Serve check: `document.title === 'FlyTracker' && document.querySelector('.readouts').textContent.includes('16344')`
- Files: `D:\git clone\FlyTracker\docs\issues\feature\31-feature-neural-flight\cleanup-ui-20261112\neural`

| page | viewport | file | overflow | probes | console |
| --- | --- | --- | --- | --- | --- |
| / | 1600x900 | neural-1600x900.png | none | `document.querySelector('.readouts')?.textContent` = 비행 설정신경 날개 (실험)조준 구간유지상태보임비행 속도0.38m/s가상 자극대기자극 횟수1회감각 입력0.0HzDNg02 출력3.6Hz도피 회로 출력0.1Hz급선회 출력3.9Hz벽 감각 입력0.0Hz운동 상태회복 중회로 연결16344개 | 1 error, 6 warnings<br>error: Failed to load resource: the server responded with a status of 404 (Not Found) (http://127.0.0.1:5181/favicon.ico)<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.<br>warning: [.WebGL-0x2f4400be7000]GL Driver Message (OpenGL, Performance, GL_CLOSE_PATH_NV, High): GPU stall due to ReadPixels (http://127.0.0.1:5181/?run=2026-11-12_180710_02-30&tag=tracking-observation&ep=1)<br>… |
| / | 390x844 (mobile, dpr 2) | neural-390x844.png | none | `document.querySelector('.readouts')?.textContent` = 비행 설정신경 날개 (실험)조준 구간유지상태보임비행 속도0.36m/s가상 자극대기자극 횟수1회감각 입력0.0HzDNg02 출력2.8Hz도피 회로 출력0.0Hz급선회 출력0.5Hz벽 감각 입력0.0Hz운동 상태회복 중회로 연결16344개 | 0 errors, 2 warnings<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead. |
