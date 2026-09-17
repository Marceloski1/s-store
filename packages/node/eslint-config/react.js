import reactHooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"

import { baseConfig } from "./base.js"

export function reactConfig({ tsconfigRootDir, ignores = [], allowExportNames = [] }) {
  return baseConfig({
    tsconfigRootDir,
    ignores,
    extends: [
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
      {
        rules: {
          "react-refresh/only-export-components": ["error", { allowConstantExport: true, allowExportNames }],
        },
      },
    ],
  })
}
