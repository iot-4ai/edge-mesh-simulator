import "./style.scss"
import * as THREE from "three"
import { initCamera, initLights, initKeybinds, orientCamera } from "./setup"
import { scene, renderer, camera, cameraControls } from "./setup"
import { loadFactory } from "./factory"
import { loadControllers, updateControllers } from "./controllers"
import { initInteract, updateInteract } from "./interact"

const clock = new THREE.Clock()

function animate() {
    requestAnimationFrame(animate)
    const delta = clock.getDelta()
    updateControllers()
    updateInteract() // move popup with node
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

async function init() {
    initCamera()
    initKeybinds()
    initInteract()
    await loadFactory()
    initLights()
    orientCamera({view: "top"})
    await loadControllers()
    renderer.render(scene, camera)
    animate()
}

init()
