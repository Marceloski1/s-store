import { StrokeIcon, type IconProps } from "./stroke-icon"

export function PlusIcon({
  size = 16,
  strokeWidth = 2.2,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundJoins={false}
      {...props}
    >
      <path d="M12 5v14M5 12h14" />
    </StrokeIcon>
  )
}
