import { StrokeIcon, type IconProps } from "./stroke-icon"

export function UsersIcon({
  size = 19,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M3 19.5c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" />
      <path d="M16 4.8a3.5 3.5 0 0 1 0 6.4M18 14.4c1.8.6 3 2.3 3 4.6" />
    </StrokeIcon>
  )
}
