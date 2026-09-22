import { StrokeIcon, type IconProps } from "./stroke-icon"

export function LogoutIcon({
  size = 15,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M14 20H6a1.5 1.5 0 0 1-1.5-1.5v-13A1.5 1.5 0 0 1 6 4h8" />
      <path d="M17 8.5 20.5 12 17 15.5M10 12h10.5" />
    </StrokeIcon>
  )
}
