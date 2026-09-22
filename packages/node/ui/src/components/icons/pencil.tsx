import { StrokeIcon, type IconProps } from "./stroke-icon"

export function PencilIcon({
  size = 15,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M4 20h4L20 8l-4-4L4 16Z" />
    </StrokeIcon>
  )
}
