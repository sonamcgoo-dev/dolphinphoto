interface BrandLogoProps {
  className?: string
  showWordmark?: boolean
}

export default function BrandLogo({ className = '', showWordmark = true }: BrandLogoProps) {
  if (!showWordmark) {
    return (
      <img
        src="/icon.png"
        alt="DolphinPhoto"
        className={`h-8 w-8 rounded-lg object-cover ${className}`.trim()}
      />
    )
  }

  return (
    <img
      src="/dolphinphoto-logo.png"
      alt="DolphinPhoto"
      className={`h-8 w-auto object-contain ${className}`.trim()}
    />
  )
}
