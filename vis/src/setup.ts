import * as THREE from "three"
import CameraControls from "camera-controls"
import { KeyboardKeyHold as KHold } from "hold-event"
import { factoryBorders, factoryOpacity, factorySize, center } from "./factory"
import { onController, hidePopup } from "./interact"

CameraControls.install({ THREE: THREE })

export const scene = new THREE.Scene()
export const renderer = new THREE.WebGLRenderer({ antialias: true })
export let camera: THREE.OrthographicCamera

export let cameraControls: CameraControls,
    factoryVis: number = 1

export const camPos: THREE.Vector3 = new THREE.Vector3(75, 100, 300)

export const COL = {
    bg: new THREE.Color(0x343044),
    node: new THREE.Color(0xb0c9ff),
    blue: new THREE.Color(0x1e90ff),
    floor: new THREE.Color(0x6a6a84),
    light: new THREE.Color(0xccccff),
    white: new THREE.Color(0xffffff),
    black: new THREE.Color(0x000000)
}

let width = window.innerWidth,
    height = window.innerHeight

export function initCamera() {
    camera = new THREE.OrthographicCamera()
    cameraControls = new CameraControls(camera, renderer.domElement)

    renderer.setSize(width, height)
    document.body.appendChild(renderer.domElement)

    window.addEventListener("resize", onWindowResize)
}

export function orientCamera({ view = "" } = {}) {
    // console.log(view, onController)
    const aspect = width / height,
        padding = 1.4
    let halfWidth = Math.max(factorySize.x / 2, (factorySize.y * aspect) / 2) * padding,
        halfHeight = halfWidth / aspect

    camera.left = -(camera.right = halfWidth)
    camera.bottom = -(camera.top = halfHeight)
    camera.updateProjectionMatrix()

    let direction: THREE.Vector3
    if (view == "default") direction = new THREE.Vector3(1, 1, 1)
    else if (view == "top") direction = new THREE.Vector3(0, 1, 0)
    else direction = camera.position.clone().sub(center)

    // move frustum near plane back:
    const distance = Math.max(factorySize.x, factorySize.y, factorySize.z) * 2
    const position = center.clone().add(direction.normalize().multiplyScalar(distance))

    if (!onController) {
        cameraControls.setLookAt(position.x, position.y, position.z, center.x, center.y, center.z, true)
        cameraControls.zoomTo(1.0, true)
    }
    if (direction.normalize().dot(new THREE.Vector3(0, 1, 0)) > 0.999) {
        // top: rotate 90deg + avoid bad rotation induced by floating point err
        cameraControls.rotateTo(Math.PI / 2, 0, true)
    }
}

export function initLights() {
    scene.background = COL.bg
    scene.add(new THREE.AmbientLight(COL.light, 0.8))

    const mainLight = new THREE.DirectionalLight(COL.white, 2.0)
    mainLight.position.set(-0, 200, 25)
    mainLight.castShadow = true
    mainLight.shadow.mapSize.set(512, 512)

    mainLight.shadow.camera.bottom = -(mainLight.shadow.camera.top = factorySize.z)
    mainLight.shadow.camera.right = -(mainLight.shadow.camera.left = factorySize.x)
    scene.add(mainLight)

    const fillLight = new THREE.DirectionalLight(new THREE.Color(COL.light), 0.5)
    fillLight.position.set(-50, 75, -50)
    scene.add(fillLight)

    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.BasicShadowMap
    mainLight.shadow.bias = -0.005
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

    const rKey = new KHold(KEYCODE.R, 16.666),
        vKey = new KHold(KEYCODE.V, 16.666),
        bKey = new KHold(KEYCODE.B, 16.666),
        tKey = new KHold(KEYCODE.T, 16.666)
    rKey.addEventListener("holdStart", () => {
        if (onController) hidePopup()
        orientCamera({ view: "default" })
    })
    vKey.addEventListener("holdEnd", () => {
        factoryVis = factoryVis === 1 ? 0.1 : 1
        factoryOpacity(factoryVis)
    })
    bKey.addEventListener("holdEnd", () => {
        factoryBorders.visible = !factoryBorders.visible
    })
    tKey.addEventListener("holdStart", () => {
        if (onController) hidePopup()
        orientCamera({ view: "top" })
    })
}

function onWindowResize() {
    width = window.innerWidth
    height = window.innerHeight
    renderer.setSize(width, height)
    orientCamera()
}
