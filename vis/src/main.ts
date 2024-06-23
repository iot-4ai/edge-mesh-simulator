import * as THREE from "three"
import { initCamera, initLights, initKeybinds } from "./setup"
import { loadFactory } from "./factory"
import { loadControllers, updateControllers } from "./controllers"
import { scene, renderer, camera, cameraControls } from "./setup"

const clock = new THREE.Clock()

function animate() {
    requestAnimationFrame(animate)
    const delta = clock.getDelta()
    updateControllers()
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

async function init() {
    initCamera()
    initLights()
    initKeybinds()
    await loadFactory()
    await loadControllers()
    renderer.render(scene, camera)
    animate()
}

init()
