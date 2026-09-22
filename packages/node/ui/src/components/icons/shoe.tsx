import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ShoeIcon({
  size = 19,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M3 15c0-4 2-7 5-7 2 0 3 1.4 3.7 3 .7 1.6 2 2.4 3.6 2.4H18c2 0 3 1 3 2.6V17H3Z" />
    </StrokeIcon>
  )
}
