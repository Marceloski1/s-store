import type { IconProps } from "./stroke-icon"

export function QuoteIcon({ size = 30, ...props }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      {...props}
    >
      <path d="M7 6h4v6a5 5 0 0 1-5 5v-3a2 2 0 0 0 2-2H7Zm7 0h4v6a5 5 0 0 1-5 5v-3a2 2 0 0 0 2-2h-1Z" />
    </svg>
  )
}
