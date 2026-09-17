import js from "@eslint/js"
import { defineConfig, globalIgnores } from "eslint/config"
import globals from "globals"
import tseslint from "typescript-eslint"

export function baseConfig({ tsconfigRootDir, ignores = [], extends: extra = [] }) {
  return defineConfig([
    globalIgnores(["dist", ...ignores]),
    {
      files: ["**/*.{ts,tsx}"],
      extends: [js.configs.recommended, tseslint.configs.recommended, ...extra],
      languageOptions: {
        globals: globals.browser,
        parserOptions: {
          tsconfigRootDir,
        },
      },
    },
  ])
}
