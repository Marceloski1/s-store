import { StrokeIcon, type IconProps } from "./stroke-icon"

export function StopwatchIcon({
  size = 22,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <circle cx="12" cy="13" r="7.5" />
      <path d="M12 13V9M9.5 3.5h5" />
    </StrokeIcon>
  )
}
