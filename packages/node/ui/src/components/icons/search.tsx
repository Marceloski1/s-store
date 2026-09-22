import { StrokeIcon, type IconProps } from "./stroke-icon"

export function SearchIcon({
  size = 17,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundJoins={false}
      {...props}
    >
      <circle cx="11" cy="11" r="7" />
      <path d="M16.4 16.4 21 21" />
    </StrokeIcon>
  )
}
