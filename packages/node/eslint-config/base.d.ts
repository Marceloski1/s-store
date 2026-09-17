import type { Linter } from "eslint"

export interface BaseConfigOptions {
  tsconfigRootDir: string
  ignores?: string[]
  extends?: Linter.Config[]
}

export function baseConfig(options: BaseConfigOptions): Linter.Config[]
