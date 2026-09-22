import { StrokeIcon, type IconProps } from "./stroke-icon"

export function WavesIcon({
  size = 22,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M3 15c2-3 4-3 6 0s4 3 6 0 4-3 6 0" />
      <path d="M3 9c2-3 4-3 6 0s4 3 6 0 4-3 6 0" />
    </StrokeIcon>
  )
}
