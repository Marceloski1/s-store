import type { ReactNode, SVGProps } from "react"

export type IconProps = Omit<
  SVGProps<SVGSVGElement>,
  "children" | "width" | "height"
> & {
  size?: number
}

type StrokeIconProps = IconProps & {
  children: ReactNode
  roundCaps?: boolean
  roundJoins?: boolean
}

export function StrokeIcon({
  size = 24,
  roundCaps = true,
  roundJoins = true,
  children,
  ...props
}: StrokeIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeLinecap={roundCaps ? "round" : undefined}
      strokeLinejoin={roundJoins ? "round" : undefined}
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  )
}
