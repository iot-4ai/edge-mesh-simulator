import * as THREE from "three"
import { initCamera, initLights, initKeybinds, orientCamera } from "./setup"
import { scene, renderer, camera, cameraControls } from "./setup"
import { loadFactory } from "./factory"
import { loadControllers, updateControllers } from "./controllers"
import { initSplash, updateProgress, removeSplash } from "./components/Progress"
import { initInteract, updateInteract } from "./interact"
import { initEdges, updateEdges } from "./edges"

const clock = new THREE.Clock()

function animate() {
    requestAnimationFrame(animate)
    const delta = clock.getDelta()
    updateControllers()
    updateEdges()
    updateInteract() // move popup with node
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

function buildProgress(): Promise<void> {
    return new Promise((resolve) => {
        initSplash()

        function getPerc() {
            fetch("http://localhost:8001/progress")
                .then((response) => response.json())
                .then((data) => {
                    const percentage = data.progress * 100
                    updateProgress(percentage)

                    if (data.progress < 1.0) requestAnimationFrame(getPerc)
                    else {
                        console.log("Build complete")
                        removeSplash()
                        resolve()
                    }
                })
        }
        getPerc()
    })
}

export async function init() {
    initCamera()
    initKeybinds()
    initInteract()
    await buildProgress() // block on build step
    await loadFactory()
    initLights()
    orientCamera({ view: "default" })
    await loadControllers()
    initEdges()
    renderer.render(scene, camera)
    animate()
}

init()
