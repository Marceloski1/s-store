// @ts-check

import tailwindcss from "@tailwindcss/vite"
import { defineConfig, envField } from "astro/config"
import vercel from "@astrojs/vercel"
import react from "@astrojs/react"

// https://astro.build/config
export default defineConfig({
  output: "server",
  adapter: vercel(),
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
