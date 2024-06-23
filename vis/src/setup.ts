import * as THREE from "three"
import CameraControls from "camera-controls"
import { KeyboardKeyHold as KHold } from "hold-event"
import { factoryBorders, factoryGroup } from "./factory"

CameraControls.install({ THREE: THREE })

export const scene = new THREE.Scene()
export const renderer = new THREE.WebGLRenderer()
export let camera: THREE.OrthographicCamera

export let cameraControls: CameraControls

export const camPos: THREE.Vector3 = new THREE.Vector3(75, 100, 300)

export const COL = {
    bg: new THREE.Color(0x343444),
    dim: new THREE.Color(0x2d3645),
    node: new THREE.Color(0x1e90ff),
    floor: new THREE.Color(0x6a6a84),
    white: new THREE.Color(0xffffff),
    black: new THREE.Color(0x000000)
}

let width = window.innerWidth,
    height = window.innerHeight

export function initCamera() {
    camera = new THREE.OrthographicCamera(width / -200, width / 200, height / 200, height / -200, 0.1, 3000)
    cameraControls = new CameraControls(camera, renderer.domElement)
    cameraControls.setPosition(camPos.x, camPos.y, camPos.z)
    cameraControls.zoomTo(fyZoom())

    renderer.setSize(width, height)
    document.body.appendChild(renderer.domElement)

    window.addEventListener("resize", onWindowResize)
}

export function initLights() {
    scene.background = COL.bg
    scene.add(new THREE.AmbientLight(COL.dim, 8))
    let directionalLight = new THREE.DirectionalLight(COL.white, 4.5)
    directionalLight.position.set(-50, 50, -50)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.set(4000, 4000)
    scene.add(directionalLight)
}
export function initKeybinds() {
    // prettier-ignore
    const KEYCODE = {
        W: 87, A: 65, S: 83, D: 68,
        ARROW_LEFT: 37, ARROW_UP: 38, ARROW_RIGHT: 39, ARROW_DOWN: 40,
        R: 82,
        V: 86,
        B: 66,
        T: 84,
    };

    // NAVIGATION
    const wKey = new KHold(KEYCODE.W, 16.666),
        aKey = new KHold(KEYCODE.A, 16.666),
        sKey = new KHold(KEYCODE.S, 16.666),
        dKey = new KHold(KEYCODE.D, 16.666)
    aKey.addEventListener("holding", (event: any) => {
        cameraControls.truck(-0.05 * event.deltaTime, 0, false)
    })
    dKey.addEventListener("holding", (event: any) => {
        cameraControls.truck(0.05 * event.deltaTime, 0, false)
    })
    wKey.addEventListener("holding", (event: any) => {
        cameraControls.forward(0.05 * event.deltaTime, false)
    })
    sKey.addEventListener("holding", (event: any) => {
        cameraControls.forward(-0.05 * event.deltaTime, false)
    })

    const leftKey = new KHold(KEYCODE.ARROW_LEFT, 100),
        rightKey = new KHold(KEYCODE.ARROW_RIGHT, 100),
        upKey = new KHold(KEYCODE.ARROW_UP, 100),
        downKey = new KHold(KEYCODE.ARROW_DOWN, 100)
    leftKey.addEventListener("holding", (event: any) => {
        cameraControls.rotate(-0.1 * THREE.MathUtils.DEG2RAD * event.deltaTime, 0, true)
    })
    rightKey.addEventListener("holding", (event: any) => {
        cameraControls.rotate(0.1 * THREE.MathUtils.DEG2RAD * event.deltaTime, 0, true)
    })
    upKey.addEventListener("holding", (event: any) => {
        cameraControls.rotate(0, -0.05 * THREE.MathUtils.DEG2RAD * event.deltaTime, true)
    })
    downKey.addEventListener("holding", (event: any) => {
        cameraControls.rotate(0, 0.05 * THREE.MathUtils.DEG2RAD * event.deltaTime, true)
    })

    // SETTINGS
    const rKey = new KHold(KEYCODE.R, 16.666),
        vKey = new KHold(KEYCODE.V, 16.666),
        bKey = new KHold(KEYCODE.B, 16.666),
        tKey = new KHold(KEYCODE.T, 16.666)
    rKey.addEventListener("holdStart", () => {
        cameraControls.setLookAt(camPos.x, camPos.y, camPos.z, 0, 0, 0, true)
        cameraControls.zoomTo(fyZoom())
    })
    vKey.addEventListener("holdEnd", () => {
        factoryGroup.visible = !factoryGroup.visible
    })
    bKey.addEventListener("holdEnd", () => {
        factoryBorders.visible = !factoryBorders.visible
    })
    tKey.addEventListener("holdStart", () => {
        cameraControls.setLookAt(camPos.x, camPos.y, camPos.z, 0, 0, 0, true)
        cameraControls.rotateTo(Math.PI / 2, 0, true)
        cameraControls.zoomTo(fxZoom(), true)
    })
}

function onWindowResize() {
    width = window.innerWidth
    height = window.innerHeight
    renderer.setSize(width, height)
    camera.left = width / -200
    camera.right = width / 200
    camera.top = height / 200
    camera.bottom = height / -200
    camera.updateProjectionMatrix()
    cameraControls.zoomTo(fxZoom(), true)
}

function fxZoom() {
    return width / height / 40
}
function fyZoom() {
    return width / height / 25
}
