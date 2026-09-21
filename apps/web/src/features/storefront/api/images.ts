const CLOUDINARY_UPLOAD_SEGMENT = "/image/upload/"

export function optimizedImageUrl(url: string, width: number): string {
  if (
    !url.includes("res.cloudinary.com") ||
    !url.includes(CLOUDINARY_UPLOAD_SEGMENT)
  ) {
    return url
  }
  return url.replace(
    CLOUDINARY_UPLOAD_SEGMENT,
    `${CLOUDINARY_UPLOAD_SEGMENT}f_auto,q_auto,c_limit,w_${width}/`
  )
}
