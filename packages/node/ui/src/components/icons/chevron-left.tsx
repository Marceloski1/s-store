import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ChevronLeftIcon({
  size = 15,
  strokeWidth = 2.2,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="m14.5 6-6 6 6 6" />
    </StrokeIcon>
  )
}
