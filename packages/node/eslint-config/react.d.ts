import type { Linter } from "eslint"

export interface ReactConfigOptions {
  tsconfigRootDir: string
  ignores?: string[]
  allowExportNames?: string[]
}

export function reactConfig(options: ReactConfigOptions): Linter.Config[]
