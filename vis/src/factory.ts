import * as THREE from "three"
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"
import { scene, COL } from "./setup"

export let factoryGroup: THREE.Group, factoryBorders: THREE.Line

let floor: THREE.Mesh
export let factorySize: THREE.Vector3 = new THREE.Vector3(),
    center: THREE.Vector3 = new THREE.Vector3(),
    boundingBox: THREE.Box3

const sceneUrl = "./assets/scene.glb",
    gltfLoader = new GLTFLoader()

export function loadFactory(): Promise<void> {
    return new Promise((resolve, reject) => {
        gltfLoader.load(
            sceneUrl,
            (gltf: any) => {
                factoryGroup = gltf.scene
                scene.add(makeFactoryBorder())
                updateFactoryGroup()
                makeBoundingBox()
                scene.add(factoryGroup)
                scene.add(makeFloor())
                resolve()
            },
            undefined,
            (error: any) => {
                console.error("Failed do load GLTF model:", error)
                reject(error)
            }
        )
    })
}

function makeFactoryBorder() {
    const tempBox = new THREE.BoxHelper(factoryGroup, COL.white)
    factoryBorders = new THREE.Line(
        tempBox.geometry.toNonIndexed(),
        new THREE.LineDashedMaterial({ color: COL.white, dashSize: 1, gapSize: 0.5 })
    )
    factoryBorders.computeLineDistances()
    factoryBorders.applyMatrix4(tempBox.matrix)
    factoryBorders.visible = false
    factoryBorders.position.set(-20, 0, 10)
    return factoryBorders
}

function updateFactoryGroup() {
    factoryGroup.traverse((child: any) => {
        if (child instanceof THREE.Mesh) {
            child.castShadow = true
        }
    })
    factoryGroup.position.set(-20, 0, 10)
}

export function factoryOpacity(opacity: number) {
    ;(floor.material as THREE.Material).transparent = opacity < 1
    ;(floor.material as THREE.Material).opacity = opacity
    factoryGroup.traverse((child: THREE.Object3D) => {
        if (child instanceof THREE.Mesh) {
            child.material.transparent = opacity < 1
            child.material.opacity = opacity
        }
    })
}

function makeBoundingBox() {
    boundingBox = new THREE.Box3().setFromObject(factoryGroup)
    boundingBox.getSize(factorySize)
    boundingBox.getCenter(center)
}

function makeFloor(border = 4) {
    const width = factorySize.z + border,
        height = factorySize.x + border
    const floorGeom = new THREE.PlaneGeometry(width, height, width, height)
    const floorMat = new THREE.MeshStandardMaterial({
        color: COL.floor,
        side: THREE.DoubleSide
    })
    floor = new THREE.Mesh(floorGeom, floorMat)
    floor.position.set(center.x, -0.001, center.z)
    floor.rotation.x = -Math.PI / 2
    floor.rotation.z = Math.PI / 2
    floor.receiveShadow = true
    return floor
}
