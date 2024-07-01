import * as THREE from "three"
import { camera, cameraControls, factoryVis } from "./setup"
import { controllerSphereMesh, controllers } from "./controllers"
import { initPopup, updatePopup } from "./components/Popup"
import { factoryOpacity } from "./factory"


let ray: THREE.Raycaster, mouse: THREE.Vector2
export let onController: string | null = null

export function initInteract() {
    initPopup()
    ray = new THREE.Raycaster()
    mouse = new THREE.Vector2()

    window.addEventListener("click", (event: MouseEvent) => {
        const obj = checkIntersect(event)
        if (obj) {
            const name = Object.keys(controllers)[obj.instanceId!]
            if (!onController) cameraControls.saveState()
            showPopup(name, event.x, event.y)
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

function showPopup(name: string, x: number, y: number) {
    const controller = controllers[name]
    updatePopup({ controller, position: { x: x + 10, y: y + 10 } })

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
    onController = name // on
    cameraControls.setTarget(pos.x, pos.y, pos.z, true)
    // if (factoryVis == 1) factoryOpacity(0.4)
}

export function hidePopup({ restore = false } = {}) {
    updatePopup({ controller: null, position: { x: 0, y: 0 } })
    if (onController) {
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

        updatePopup({ controller, position: { x: x + 10, y: y + 10 } })
    }
}
