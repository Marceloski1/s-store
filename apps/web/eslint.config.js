import { reactConfig } from "@workspace/eslint-config/react"

export default reactConfig({
  tsconfigRootDir: import.meta.dirname,
  ignores: [".astro"],
})
