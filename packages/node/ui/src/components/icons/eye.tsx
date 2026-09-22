import { StrokeIcon, type IconProps } from "./stroke-icon"

export function EyeIcon({ size = 19, strokeWidth = 1.8, ...props }: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M2.5 12S6 6 12 6s9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
      <circle cx="12" cy="12" r="2.8" />
    </StrokeIcon>
  )
}
