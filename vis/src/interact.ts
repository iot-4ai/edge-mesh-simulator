import * as THREE from "three"
import { camera, cameraControls, factoryVis, orientCamera } from "./setup"
import { controllerSphereMesh, controllers } from "./controllers"
import { factoryOpacity } from "./factory"

let ray: THREE.Raycaster, mouse: THREE.Vector2
export let onController: string | null = null
const popup = document.getElementById("popup")

export function initInteract() {
    ray = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    window.addEventListener("click", (event: MouseEvent) => {
        const obj = checkIntersect(event)
        if (obj) {
            const ID = obj.instanceId
            const name = Object.keys(controllers)[ID!]
            if (!onController) cameraControls.saveState()
            showPopup(name, event)
        } else hidePopup({ restore: true })
    })
    window.addEventListener("keydown", (event: KeyboardEvent) => {
        if (event.key == "Escape") hidePopup({ restore: true })
    })
}

function checkIntersect(event: MouseEvent) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1
    ray.setFromCamera(mouse, camera)
    const intersects = ray.intersectObject(controllerSphereMesh)

    return intersects.length > 0 ? intersects[0] : false
}

function showPopup(name: string, event: MouseEvent) {
    if (onController === name) return

    const controller = controllers[name]
    if (popup) {
        // contents
        popup.innerHTML = `
        <h3>${controller.name}</h3>
        <p>IP: ${controller.ip}</p>
        <p>Signal: ${controller.signal}</p>
        `
        popup.style.display = "block"
        popup.style.left = `${event.clientX + 10}px`
        popup.style.top = `${event.clientY + 10}px`
    }

    const pos = new THREE.Vector3(controller.pos.x - 20, controller.pos.z, -controller.pos.y + 10)
    // pan (truck) rotate, and zoom onto controller
    const targetPos = new THREE.Vector3()
    cameraControls.getTarget(targetPos)
    const panDelta = new THREE.Vector3().subVectors(pos, targetPos)
    cameraControls.truck(panDelta.x, panDelta.y, true)

    if (!onController) {
        cameraControls.rotate(Math.PI / 6, 0, true)
        cameraControls.zoom(camera.zoom * 2, true)
        onController = name // on
    }
    cameraControls.setTarget(pos.x, pos.y, pos.z, true)
    // if (factoryVis == 1) factoryOpacity(0.4)
}

export function hidePopup({ restore = false } = {}) {
    if (onController) {
        if (popup) popup.style.display = "none"
        onController = null
        if (restore) cameraControls.reset(true)
        // orientCamera() // ensure fit
        factoryOpacity(factoryVis)
    }
}

export function updateInteract() {
    if (onController) {
        const controller = controllers[onController]
        const screenPosition = new THREE.Vector3(controller.pos.x - 20, controller.pos.z, -controller.pos.y + 10)
        screenPosition.project(camera)

        const x = (screenPosition.x * 0.5 + 0.5) * window.innerWidth
        const y = -(screenPosition.y * 0.5 - 0.5) * window.innerHeight

        if (popup) {
            popup.style.left = `${x + 10}px`
            popup.style.top = `${y + 10}px`
        }
    }
}
