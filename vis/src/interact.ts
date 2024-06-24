import * as THREE from "three"
import { camera, cameraControls, factoryVis } from "./setup"
import { controllerMesh, controllers } from "./controllers"
import { factoryOpacity } from "./factory"

let ray: THREE.Raycaster, mouse: THREE.Vector2
let selectedController: string | null = null,
    onController: boolean = false
const popup = document.getElementById("popup")

export function initInteract() {
    ray = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    window.addEventListener("click", (event: MouseEvent) => {
        const obj = checkIntersect(event)
        if (obj) {
            const ID = obj.instanceId
            const controllerName = Object.keys(controllers)[ID!]
            if (!onController) cameraControls.saveState()
            showPopup(controllerName, event)
            if (!onController) onController = true
        } else hideControllerInfo()
    })
    window.addEventListener("keydown", (event: KeyboardEvent) => {
        if (event.key === "Escape") hideControllerInfo()
    })
}

function checkIntersect(event: MouseEvent) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1
    ray.setFromCamera(mouse, camera)
    const intersects = ray.intersectObject(controllerMesh)

    return intersects.length > 0 ? intersects[0] : false
}

function showPopup(controllerName: string, event: MouseEvent) {
    if (selectedController === controllerName) return

    selectedController = controllerName
    const controller = controllers[controllerName]

    if (popup) { // contents
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
    }
    cameraControls.setTarget(pos.x, pos.y, pos.z, true)
    if (factoryVis == 1) factoryOpacity(0.4)
}

function hideControllerInfo() {
    if (selectedController) {
        if (popup) popup.style.display = "none"
        selectedController = null
        onController = false
        cameraControls.reset(true)
        factoryOpacity(factoryVis)
    }
}

export function updateInteract() {
    if (selectedController) {
        const controller = controllers[selectedController]
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
