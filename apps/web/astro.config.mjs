// @ts-check

import tailwindcss from "@tailwindcss/vite"
import { defineConfig, envField } from "astro/config"
import node from "@astrojs/node"
import react from "@astrojs/react"

// https://astro.build/config
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  env: {
    schema: {
      API_URL: envField.string({
        context: "server",
        access: "public",
        url: true,
      }),
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [react()],
})
