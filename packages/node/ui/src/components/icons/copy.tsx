import { StrokeIcon, type IconProps } from "./stroke-icon"

export function CopyIcon({
  size = 15,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon
      size={size}
      strokeWidth={strokeWidth}
      roundCaps={false}
      {...props}
    >
      <rect x="8.5" y="8.5" width="11" height="11" rx="1.5" />
      <path d="M15.5 5.5H6A1.5 1.5 0 0 0 4.5 7v9.5" />
    </StrokeIcon>
  )
}
