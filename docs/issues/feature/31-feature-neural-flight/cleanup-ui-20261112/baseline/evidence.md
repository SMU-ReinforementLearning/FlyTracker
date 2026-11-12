# UI evidence — baseline

- Generated: 2026-11-12T13:57:23.637Z
- Base: `http://127.0.0.1:5181`
- Pages: `http://127.0.0.1:5181/?run=2026-11-11_133858_baseline&tag=baseline&ep=1`
- Commit: 7237428 (dirty)
- Chrome: Chrome/157.0.8103.40 (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- Viewports: 1600x900, 390x844 (mobile, dpr 2)
- Ready: `document.querySelector('.readouts') !== null && document.querySelector('canvas') !== null` · settle 800 ms · reduced-motion on · per-shot timeout 45000 ms
- Serve check: `document.title === 'FlyTracker' && document.querySelector('.readouts').textContent.includes('포획 진행')`
- Files: `D:\git clone\FlyTracker\docs\issues\feature\31-feature-neural-flight\cleanup-ui-20261112\baseline`

| page | viewport | file | overflow | probes | console |
| --- | --- | --- | --- | --- | --- |
| / | 1600x900 | baseline-1600x900.png | none | `document.querySelector('.readouts')?.textContent` = 상태안 보임조준 오차39.6°거리2.28m포획 진행0%초파리평시프레임42 / 170 | 1 error, 6 warnings<br>error: Failed to load resource: the server responded with a status of 404 (Not Found) (http://127.0.0.1:5181/favicon.ico)<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.<br>warning: [.WebGL-0x640400bb4a00]GL Driver Message (OpenGL, Performance, GL_CLOSE_PATH_NV, High): GPU stall due to ReadPixels (http://127.0.0.1:5181/?run=2026-11-11_133858_baseline&tag=baseline&ep=1)<br>… |
| / | 390x844 (mobile, dpr 2) | baseline-390x844.png | none | `document.querySelector('.readouts')?.textContent` = 상태안 보임조준 오차41.7°거리2.26m포획 진행0%초파리평시프레임48 / 170 | 0 errors, 2 warnings<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.<br>warning: THREE.Clock: This module has been deprecated. Please use THREE.Timer instead. |
