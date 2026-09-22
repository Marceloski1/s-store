import { StrokeIcon, type IconProps } from "./stroke-icon"

export function InstagramIcon({
  size = 17,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundCaps={false}
      roundJoins={false}
      {...props}
    >
      <rect x="3.5" y="3.5" width="17" height="17" rx="5" />
      <circle cx="12" cy="12" r="4" />
    </StrokeIcon>
  )
}
