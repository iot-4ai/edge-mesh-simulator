import { defineConfig } from "astro/config"
import react from "@astrojs/react"

export default defineConfig({
    integrations: [react()],
    vite: {
        logLevel: "warn"
    },
    server: {
        open: true,
        port: 8000
    }
})
