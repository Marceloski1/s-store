import { StrokeIcon, type IconProps } from "./stroke-icon"

export function CloseIcon({
  size = 12,
  strokeWidth = 2.4,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundJoins={false}
      {...props}
    >
      <path d="M6 6l12 12M18 6 6 18" />
    </StrokeIcon>
  )
}
