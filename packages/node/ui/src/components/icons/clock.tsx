import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ClockIcon({
  size = 15,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundJoins={false}
      {...props}
    >
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3.2 2" />
    </StrokeIcon>
  )
}
