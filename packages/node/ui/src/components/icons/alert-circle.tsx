import { StrokeIcon, type IconProps } from "./stroke-icon"

export function AlertCircleIcon({
  size = 17,
  strokeWidth = 2,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 8v4.5M12 16h0" />
    </StrokeIcon>
  )
}
