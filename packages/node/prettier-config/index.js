import * as astroPlugin from "prettier-plugin-astro"
import * as tailwindPlugin from "prettier-plugin-tailwindcss"

export function prettierConfig({ tailwindStylesheet } = {}) {
  return {
    endOfLine: "lf",
    semi: false,
    singleQuote: false,
    tabWidth: 2,
    trailingComma: "es5",
    printWidth: 80,
    plugins: [astroPlugin, tailwindPlugin],
    tailwindStylesheet,
    tailwindFunctions: ["cn", "cva"],
    overrides: [
      {
        files: "*.astro",
        options: {
          parser: "astro",
        },
      },
    ],
  }
}
