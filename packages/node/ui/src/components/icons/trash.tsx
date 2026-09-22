import { StrokeIcon, type IconProps } from "./stroke-icon"

export function TrashIcon({
  size = 15,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M4 7h16M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13" />
    </StrokeIcon>
  )
}
