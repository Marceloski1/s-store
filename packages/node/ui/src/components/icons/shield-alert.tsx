import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ShieldAlertIcon({
  size = 18,
  strokeWidth = 1.9,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M12 3.5 19 6v6c0 4-3 7-7 8.5C8 19 5 16 5 12V6Z" />
      <path d="M12 9v4M12 16h0" />
    </StrokeIcon>
  )
}
