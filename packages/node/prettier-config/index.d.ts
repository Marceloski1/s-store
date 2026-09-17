import type { Config } from "prettier"

export interface PrettierConfigOptions {
  tailwindStylesheet?: string
}

export function prettierConfig(options?: PrettierConfigOptions): Config
