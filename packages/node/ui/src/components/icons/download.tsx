import { StrokeIcon, type IconProps } from "./stroke-icon"

export function DownloadIcon({
  size = 16,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M12 4v11m0 0-4-4m4 4 4-4" />
      <path d="M4 17v2.5h16V17" />
    </StrokeIcon>
  )
}
