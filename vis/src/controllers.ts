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

export let controllers: { [key: string]: Controller } = {}
export let controllerMesh: THREE.InstancedMesh, controllerSphereMesh: THREE.InstancedMesh
let edgeMesh: THREE.LineSegments,
    edges: Array<[string, string]> = []

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
    const pointGeometry = new THREE.SphereGeometry(0.2, 10, 10),
        sphereGeometry = new THREE.SphereGeometry(1.25, 20, 20),
        pointMaterial = new THREE.MeshBasicMaterial({ color: COL.node }),
        sphereMaterial = new THREE.MeshBasicMaterial({
            color: COL.blue,
            transparent: true,
            opacity: 0.3
        })
    const controllerCount = Object.keys(controllers).length
    controllerMesh = new THREE.InstancedMesh(pointGeometry, pointMaterial, controllerCount)
    controllerSphereMesh = new THREE.InstancedMesh(sphereGeometry, sphereMaterial, controllerCount)

    let index = 0
    const tmpMatrix = new THREE.Matrix4()
    Object.values(controllers).forEach((item: Controller) => {
        tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
        controllerMesh.setMatrixAt(index, tmpMatrix)
        controllerSphereMesh.setMatrixAt(index, tmpMatrix)
        index++
    })

    controllerMesh.position.set(-20, 0, 10)
    controllerSphereMesh.position.set(-20, 0, 10)
    controllerMesh.instanceMatrix.needsUpdate = controllerSphereMesh.instanceMatrix.needsUpdate = true
    scene.add(controllerMesh, controllerSphereMesh)
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
    updateControllerPos()
    updateEdges()
}

function updateControllerPos() {
    if (!controllerMesh || !controllerSphereMesh) return
    const tmpMatrix = new THREE.Matrix4()
    let index = 0
    Object.values(controllers).forEach((item: Controller) => {
        tmpMatrix.setPosition(item.pos.x, item.pos.z, -item.pos.y)
        controllerMesh.setMatrixAt(index, tmpMatrix)
        controllerSphereMesh.setMatrixAt(index, tmpMatrix)
        index++
    })
    controllerMesh.instanceMatrix.needsUpdate = true
    controllerSphereMesh.instanceMatrix.needsUpdate = true
}

function updateEdges() {
    const positions: Array<number> = []
    edges.forEach((edge) => {
        const [from, to] = edge,
            fromPos = controllers[from].pos,
            toPos = controllers[to].pos
        positions.push(fromPos.x, fromPos.z, -fromPos.y, toPos.x, toPos.z, -toPos.y)
    })
    if (edgeMesh && edgeMesh.geometry)
        edgeMesh.geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3))
}
