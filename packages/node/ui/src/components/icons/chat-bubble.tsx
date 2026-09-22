import { StrokeIcon, type IconProps } from "./stroke-icon"

export function ChatBubbleIcon({
  size = 15,
  strokeWidth = 1.8,
  ...props
}: IconProps) {
  return (
    <StrokeIcon size={size} strokeWidth={strokeWidth} {...props}>
      <path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3.5 20.5l1.7-5A8.4 8.4 0 1 1 21 11.5Z" />
    </StrokeIcon>
  )
}
