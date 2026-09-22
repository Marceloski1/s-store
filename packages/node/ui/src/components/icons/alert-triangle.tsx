import { StrokeIcon, type IconProps } from "./stroke-icon"

export function AlertTriangleIcon({
  size = 19,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M12 4 21 19H3Z" />
      <path d="M12 10v4M12 16.5h0" />
    </StrokeIcon>
  )
}
