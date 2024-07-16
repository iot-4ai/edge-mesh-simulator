import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import "./styles.sass"

interface Progress {
    value: number
    step: string
}

interface Splash {
    build: Progress
    signal: Progress
}

const Bar: Component<{ progress: Progress}> = ({ progress: {value, step} }) => (
    <div className="progress-container">
        <div className={`progress-label ${value == 0 ? "idle" : ""}`}>
            {step}{value === 1 ? "" : "..."}
        </div>
        <div className="progress-bar">
            <div
                className={`progress-fill ${value == 1 ? "complete" : ""}`}
                style={{ width: `${value * 100}%` }}
            ></div>
        </div>
    </div>
)

const Splash: Component<Splash> = ({ build, signal }) => {
    return (
        <div className="progress">
            <Bar progress={build} />
            <Bar progress={signal} />
        </div>
    )
}

let splash: ReactDOM.Root

export function initSplash() {
    const parent = document.body.appendChild(document.createElement("div"))
    splash = ReactDOM.createRoot(parent)
}

export function updateProgress(build: Progress, signal: Progress) {
    splash.render(<Splash build={build} signal={signal} />)
}

export function removeSplash() {
    if (splash) splash.unmount()
}

export default Splash
