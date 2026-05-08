interface LandingMediaBackgroundProps {
  imageSrc: string
  videoSrc?: string
  alt?: string
  className?: string
  mediaClassName?: string
  overlayClassName?: string
  imageLoading?: 'eager' | 'lazy'
}

function getVideoType(videoSrc: string): string {
  return videoSrc.endsWith('.webm') ? 'video/webm' : 'video/mp4'
}

export default function LandingMediaBackground({
  imageSrc,
  videoSrc,
  alt = '',
  className = '',
  mediaClassName = 'h-full w-full object-cover',
  overlayClassName,
  imageLoading = 'lazy',
}: LandingMediaBackgroundProps) {
  return (
    <div className={className}>
      {videoSrc ? (
        <video
          className={mediaClassName}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          poster={imageSrc}
          aria-hidden={alt ? undefined : true}
        >
          <source src={videoSrc} type={getVideoType(videoSrc)} />
        </video>
      ) : (
        <img
          src={imageSrc}
          alt={alt}
          className={mediaClassName}
          loading={imageLoading}
        />
      )}
      <div className={overlayClassName} />
    </div>
  )
}
