import { useEffect, useState } from 'react'
import { Image as ImageIcon, Loader2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import { useLanguage } from '@/i18n'

interface AuthenticatedStoryboardShotImageProps {
  projectId: string
  shotId: string
  alt: string
  className: string
  fallbackLabel?: string
}

export function AuthenticatedStoryboardShotImage({
  projectId,
  shotId,
  alt,
  className,
  fallbackLabel,
}: AuthenticatedStoryboardShotImageProps) {
  const { t } = useLanguage()
  const resolvedFallbackLabel = fallbackLabel ?? t('components.storyboard.authenticatedShotImage.noThumbnail')
  const [src, setSrc] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let active = true
    let objectUrl: string | null = null

    const load = async () => {
      if (!projectId || !shotId) {
        if (active) {
          setSrc(null)
          setIsLoading(false)
        }
        return
      }

      setIsLoading(true)

      const tryLoad = async (type: 'thumbnail' | 'image') => {
        const blob = await storyboardApi.fetchStoryboardShotImageBlob(projectId, shotId, type)
        return URL.createObjectURL(blob)
      }

      try {
        objectUrl = await tryLoad('thumbnail')
      } catch (thumbError) {
        if (import.meta.env.DEV) {
          console.warn(
            `[AuthenticatedStoryboardShotImage] Thumbnail fetch failed for shot ${shotId}:`,
            (thumbError as { response?: { status?: number } })?.response?.status ?? thumbError
          )
        }
        try {
          objectUrl = await tryLoad('image')
        } catch (imageError) {
          if (import.meta.env.DEV) {
            console.warn(
              `[AuthenticatedStoryboardShotImage] Image fetch also failed for shot ${shotId}:`,
              (imageError as { response?: { status?: number } })?.response?.status ?? imageError
            )
          }
          objectUrl = null
        }
      }

      if (!active) {
        if (objectUrl) URL.revokeObjectURL(objectUrl)
        return
      }

      setSrc(objectUrl)
      setIsLoading(false)
    }

    void load()

    return () => {
      active = false
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [projectId, shotId])

  if (src) {
    return <img src={src} alt={alt} className={className} />
  }

  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-slate-500">
      {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <ImageIcon className="h-5 w-5 opacity-70" />}
      <span className="text-[11px] text-center">{isLoading ? t('components.storyboard.authenticatedShotImage.loading') : resolvedFallbackLabel}</span>
    </div>
  )
}
