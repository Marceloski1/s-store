import { StrokeIcon, type IconProps } from "./stroke-icon"

export function UploadIcon({
  size = 22,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" />
      <path d="M4 16v2.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V16" />
    </StrokeIcon>
  )
}
