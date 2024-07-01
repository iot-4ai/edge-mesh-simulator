import * as THREE from "three"
import { camera, cameraControls, factoryVis } from "./setup"
import { controllerSphereMesh, controllers } from "./controllers"
import { initPopup, updatePopup } from "./components/Popup"
import { factoryOpacity, factoryGroup } from "./factory"

let ray: THREE.Raycaster, mouse: THREE.Vector2
export let onController: string | null = null,
overPopup: boolean = false

export function initInteract() {
    initPopup()
    ray = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    window.addEventListener("click", (event: MouseEvent) => {
        const obj = checkIntersect(event)
        if (obj) {
            const name = Object.keys(controllers)[obj.instanceId!]
            if (!onController) cameraControls.saveState()
            showPopup(name)
        } else if (!overPopup) hidePopup({ restore: true })
    })
    window.addEventListener("keydown", (event: KeyboardEvent) => {
        if (event.key == "Escape") hidePopup({ restore: true })
    })
    window.addEventListener("mousemove", onPopupHover)
}

function checkIntersect(event: MouseEvent) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1
    ray.setFromCamera(mouse, camera)
    let occluded = ray.intersectObject(factoryGroup, true),
        intersects = ray.intersectObject(controllerSphereMesh)
    if (intersects.length > 0) {
        if (occluded.length > 0 && occluded[0].distance < intersects[0].distance) factoryOpacity(0.4)
        return intersects.length > 0 ? intersects[0] : false
    }
    else return false
}

function onPopupHover(event: MouseEvent) { // TODO: effects
    const popup = document.getElementById("popup")
    if (popup) {
        const rect = popup.getBoundingClientRect()
        overPopup = event.clientX >= rect.left && event.clientX <= rect.right &&
                       event.clientY >= rect.top && event.clientY <= rect.bottom
    }
}

function showPopup(name: string) {
    if (onController == name) return
    const controller = controllers[name],
        pos = new THREE.Vector3(controller.pos.x - 20, controller.pos.z, -controller.pos.y + 10)
    const x = (pos.x / 2 + 0.5) * window.innerWidth,
        y = -(pos.y / 2 - 0.5) * window.innerHeight

    updatePopup({ controller, position: { x: x + 10, y: y + 10 } })
    cameraControls.truck(pos.x, pos.y, true)
    if (!onController) cameraControls.zoom(camera.zoom * 2, true)

    onController = name // on
    cameraControls.setTarget(pos.x, pos.y, pos.z, true)
}

export function hidePopup({ restore = false } = {}) {
    updatePopup({ controller: null, position: { x: 0, y: 0 } })
    if (onController) {
        onController = null
        if (restore) cameraControls.reset(true)
        factoryOpacity(factoryVis)
    }
}

export function updateInteract() {
    if (onController) {
        const controller = controllers[onController],
            pos = new THREE.Vector3(controller.pos.x - 20, controller.pos.z, -controller.pos.y + 10)
        pos.project(camera)

        const x = (pos.x / 2 + 0.5) * window.innerWidth,
            y = -(pos.y / 2 - 0.5) * window.innerHeight

        updatePopup({ controller, position: { x: x + 10, y: y + 10 } })
    }
}