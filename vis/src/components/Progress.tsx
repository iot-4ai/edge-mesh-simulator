import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import "./styles.sass"

interface Splash {
    progress: number
    step: string
}

const Splash: Component<Splash> = ({ progress, step }) => {
    return (
        <div id="progress">
            <div id="progress-label">{step}{progress != 1.0 ? "..." : "."}</div>
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

export function updateProgress(progress: number, step: string) {
    splashRoot.render(<Splash progress={progress} step={step} />)
}

export function removeSplash() {
    splashRoot.unmount()
}

export default Splash