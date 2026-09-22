import { StrokeIcon, type IconProps } from "./stroke-icon"

export function BoltIcon({
  size = 22,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M13 3 5 13.5h5l-1 7.5 8-10.5h-5Z" />
    </StrokeIcon>
  )
}
