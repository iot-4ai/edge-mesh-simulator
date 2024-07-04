import { FC as Component } from "react"
import ReactDOM from "react-dom/client"
import "./styles.sass"

interface Controller {
    name: string
    ip: string
    signal: number
}

interface Popup {
    controller: Controller | null
    position: { x: number; y: number }
}

const Popup: Component<Popup> = ({ controller, position }) => {
    if (!controller) return null

    return (
        <div id="popup" style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
        }}>
            <h3 id="popup-title">{controller.name}</h3>
            <p id="popup-info">IP: {controller.ip}</p>
            <p id="popup-info">Signal: {controller.signal}</p>
        </div>
    )
}

let popupRoot: ReactDOM.Root

export function initPopup() {
    const parent = document.body.appendChild(document.createElement("div"))
    popupRoot = ReactDOM.createRoot(parent)
}

export function updatePopup(props: Popup) {
    popupRoot.render(<Popup {...props} />)
}

export default Popup