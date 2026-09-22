import { StrokeIcon, type IconProps } from "./stroke-icon"

export function CheckIcon({
  size = 17,
  strokeWidth = 2.4,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="m5 12.5 4.5 4.5L19 7.5" />
    </StrokeIcon>
  )
}
