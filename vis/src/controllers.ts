import * as THREE from "three"
import axios from "axios"
import { scene, COL } from "./setup"

interface Controller {
    name: string
    comm: string
    pos: { x: number; y: number; z: number }
    orient: { roll: number; pitch: number; yaw: number }
    ip: string
    signal: number
}

let controllers: { [key: string]: Controller } = {}
let controllerMesh: THREE.InstancedMesh
let edgeMesh: THREE.LineSegments
let edges: Array<[string, string]> = []

async function getControllers(): Promise<{ [key: string]: Controller }> {
    try {
        const response = await axios.get("http://localhost:8001/controllers")
        return response.data.reduce((acc: { [key: string]: Controller }, item: any) => {
            acc[item.name] = {
                name: item.name,
                comm: item.comm,
                pos: item.pos,
                orient: item.orient,
                ip: item.ip,
                signal: item.signal
            }
            return acc
        }, {})
    } catch (error) {
        console.error("Error fetching data:", error)
        return {}
    }
}

export async function loadControllers() {
    controllers = await getControllers()
    setupControllerMesh()
    setupEdgeMesh()
    updateControllers()
}

function setupControllerMesh() {
    const sphereRadius = 0.4
    const sphereGeometry = new THREE.SphereGeometry(sphereRadius, 32, 32)
    const material = new THREE.MeshBasicMaterial({ color: COL.node })
    controllerMesh = new THREE.InstancedMesh(sphereGeometry, material, Object.keys(controllers).length)
    let index = 0
    const tmpMatrix = new THREE.Matrix4()
    Object.values(controllers).forEach((item: Controller) => {
        tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
        controllerMesh.setMatrixAt(index, tmpMatrix)
        index++
    })
    controllerMesh.position.set(-20, 0, 10)
    controllerMesh.instanceMatrix.needsUpdate = true
    scene.add(controllerMesh)
}

function setupEdgeMesh() {
    const edgeGeometry = new THREE.BufferGeometry()
    const positions: Array<number> = []
    edgeGeometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3))
    const edgeMaterial = new THREE.LineBasicMaterial({ color: COL.black })
    edgeMesh = new THREE.LineSegments(edgeGeometry, edgeMaterial)
    edgeMesh.position.set(-20, 0, 10)
    scene.add(edgeMesh)
}

export function updateControllers() {
    updateControllerPositions()
    updateEdges()
}

function updateControllerPositions() {
    if (!controllerMesh) return
    const tmpMatrix = new THREE.Matrix4()
    let index = 0
    Object.values(controllers).forEach((item: Controller) => {
        tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
        controllerMesh.setMatrixAt(index, tmpMatrix)
        index++
    })
    controllerMesh.instanceMatrix.needsUpdate = true
}

function updateEdges() {
    const positions: Array<number> = []
    edges.forEach((edge) => {
        const [from, to] = edge
        const fromPos = controllers[from].pos
        const toPos = controllers[to].pos
        positions.push(fromPos.x, fromPos.z, -fromPos.y, toPos.x, toPos.z, -toPos.y)
    })
    if (edgeMesh && edgeMesh.geometry)
        edgeMesh.geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3))
}
