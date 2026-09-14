// @ts-check

import tailwindcss from "@tailwindcss/vite"
import { defineConfig, envField } from "astro/config"
import react from "@astrojs/react"

// https://astro.build/config
export default defineConfig({
  env: {
    schema: {
      PUBLIC_API_URL: envField.string({
        context: "client",
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
