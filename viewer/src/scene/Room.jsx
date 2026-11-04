import { useMemo } from 'react'
import * as THREE from 'three'

const GRID_STEP = 0.5 // m

function floorGrid(w, d) {
  const pts = []
  for (let x = -w / 2; x <= w / 2 + 1e-6; x += GRID_STEP) pts.push(x, 0, -d / 2, x, 0, d / 2)
  for (let z = -d / 2; z <= d / 2 + 1e-6; z += GRID_STEP) pts.push(-w / 2, 0, z, w / 2, 0, z)
  const g = new THREE.BufferGeometry()
  g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
  return g
}

function axes(len) {
  const g = new THREE.BufferGeometry()
  g.setAttribute('position', new THREE.Float32BufferAttribute([0, 0.001, 0, len, 0.001, 0, 0, 0.001, 0, 0, len, 0, 0, 0.001, 0, 0, 0.001, len], 3))
  g.setAttribute('color', new THREE.Float32BufferAttribute([0.9, 0.3, 0.3, 0.9, 0.3, 0.3, 0.3, 0.75, 0.4, 0.3, 0.75, 0.4, 0.3, 0.5, 0.95, 0.3, 0.5, 0.95], 3))
  return g
}

/** 바닥 중심이 원점인 방. 바닥 격자는 0.5m 간격, 원점의 짧은 축은 x 빨강, y 초록, z 파랑. */
export function Room({ size, colors, showAxes = true }) {
  const [w, h, d] = size
  const grid = useMemo(() => floorGrid(w, d), [w, d])
  const edges = useMemo(() => new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)), [w, h, d])
  const axisGeo = useMemo(() => axes(0.3), [])
  return (
    <group>
      <lineSegments geometry={grid}>
        <lineBasicMaterial color={colors.grid} />
      </lineSegments>
      <lineSegments geometry={edges} position={[0, h / 2, 0]}>
        <lineBasicMaterial color={colors.room} />
      </lineSegments>
      {showAxes && (
        <lineSegments geometry={axisGeo}>
          <lineBasicMaterial vertexColors />
        </lineSegments>
      )}
    </group>
  )
}
