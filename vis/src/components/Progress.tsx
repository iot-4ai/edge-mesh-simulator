import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import "./styles.sass"


interface Splash {
    progress: number
}

const Splash: Component<Splash> = ({ progress }) => {
    return (
        <div id="progress">
            <div id="progress-label">Building... {progress.toFixed(2)}%</div>
            <div id="progress-div">
                <div id="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
        </div>
    )
}

let splashRoot: ReactDOM.Root

export function initSplash() {
    const parent = document.body.appendChild(document.createElement("div"))
    splashRoot = ReactDOM.createRoot(parent)
}

export function updateProgress(progress: number) {
    splashRoot.render(<Splash progress={progress} />)
}

export function removeSplash() {
    splashRoot.unmount()
}

export default Splash
