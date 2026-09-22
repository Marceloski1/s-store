import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ShareIcon({
  size = 17,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M12 16V4m0 0L8 8m4-4 4 4" />
      <path d="M5 15v3.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V15" />
    </StrokeIcon>
  )
}
