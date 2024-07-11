import * as THREE from "three"
import { controllers, Controller } from "./controllers"
import { scene } from "./setup"

const MAX_VERT = 10000
let lineMesh: THREE.LineSegments

export function initEdges() {
    const geometry = new THREE.BufferGeometry(),
        positions = new Float32Array(MAX_VERT * 6), // 3<x,y,z> * 2
        colors = new Float32Array(MAX_VERT * 6) // 3<r,g,b> * 2

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3))
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3))

    const material = new THREE.LineBasicMaterial({ vertexColors: true })
    lineMesh = new THREE.LineSegments(geometry, material)
    lineMesh.position.set(-20, 0, 10)
    scene.add(lineMesh)
}

export function updateEdges() {
    const { position, color } = lineMesh.geometry.attributes,
        cVals = Object.values(controllers)
    let lines = 0

    for (let a = 0; a < cVals.length && lines < MAX_VERT; a++) {
        for (let b = a + 1; b < cVals.length && lines < MAX_VERT; b++) {
            const stren = Math.min(cVals[a].hears[cVals[b].name], cVals[b].hears[cVals[a].name])
            if (stren > 0) {
                updateLine(lines, cVals[a], cVals[b], stren)
                lines++
            }
        }
    }
    position.needsUpdate = color.needsUpdate = true
}

function updateLine(index: number, cA: Controller, cB: Controller, stren: number) {
    const { position, color } = lineMesh.geometry.attributes
    position.array.set([cA.pos.x, cA.pos.z, -cA.pos.y, cB.pos.x, cB.pos.z, -cB.pos.y], index * 6)
    const { r, g, b } = getLineColor(stren)
    color.array.set([r, g, b, r, g, b], index * 6)
}

function getLineColor(stren: number): THREE.Color {
    if (stren < 33) return new THREE.Color(1, 0, 0)
    if (stren < 66) return new THREE.Color(1, 1, 0)
    return new THREE.Color(0, 1, 0)
}
