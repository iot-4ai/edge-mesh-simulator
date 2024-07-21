import * as THREE from "three"
import { initCamera, initLights, initKeybinds, orientCamera } from "./setup"
import { scene, renderer, camera, cameraControls } from "./setup"
import { loadFactory } from "./factory"
import { loadControllers, updateControllers } from "./controllers"
import { initSplash, updateProgress, removeSplash } from "./components/Progress"
import { initInteract, updateInteract } from "./interact"
import { initEdges, updateEdges } from "./edges"

const clock = new THREE.Clock(),
    URL = "http://localhost:8001"

function animate() {
    requestAnimationFrame(animate)
    const delta = clock.getDelta()
    updateControllers()
    updateEdges()
    updateInteract() // move popup with node
    cameraControls.update(delta)
    renderer.render(scene, camera)
}

async function buildProgress(): Promise<void> {
    const getData = () => { return fetch(`${URL}/progress`).then((res) => res.json()) }
    let check = await getData()
    if (check.build.value == 1.0) return
    return new Promise((resolve) => {
        initSplash()
        function getProgress() {
            getData().then((data) => {
                    updateProgress(data.build, data.signal)

                    if (data.build.value < 1.0 || data.signal.value < 1.0) {
                        requestAnimationFrame(getProgress)
                    }
                    else resolve()
                })
        }
        getProgress()
    })
}

export async function init() {
    initCamera()
    initKeybinds()
    initInteract()
    await buildProgress() // block on build step
    await loadFactory()
    setTimeout(() => removeSplash(), 500)
    initLights()
    orientCamera({ view: "default" })
    await loadControllers()
    initEdges()
    renderer.render(scene, camera)
    animate()
}

init()
