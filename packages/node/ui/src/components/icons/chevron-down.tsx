import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ChevronDownIcon({
  size = 13,
  strokeWidth = 2.2,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="m6 9.5 6 6 6-6" />
    </StrokeIcon>
  )
}
