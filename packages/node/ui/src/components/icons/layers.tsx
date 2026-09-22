import { StrokeIcon, type IconProps } from "./stroke-icon"

export function LayersIcon({
  size = 19,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M4 7.5 12 3.5l8 4-8 4Z" />
      <path d="m4 12.5 8 4 8-4" />
    </StrokeIcon>
  )
}
