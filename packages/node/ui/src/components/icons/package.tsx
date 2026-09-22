import { StrokeIcon, type IconProps } from "./stroke-icon"

export function PackageIcon({
  size = 22,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M4 8.5 12 4l8 4.5-8 4.5Z" />
      <path d="M4 8.5v7L12 20l8-4.5v-7" />
    </StrokeIcon>
  )
}
