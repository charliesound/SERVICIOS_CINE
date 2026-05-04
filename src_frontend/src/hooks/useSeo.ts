import { useEffect } from 'react'
import { applySeo, type SeoConfig } from '@/utils/seo'

export function useSeo(config: SeoConfig) {
  const structuredDataKey = JSON.stringify(config.structuredData ?? null)
  const keywordsKey = JSON.stringify(config.keywords ?? [])

  useEffect(() => {
    applySeo(config)
  }, [config.title, config.description, config.path, config.image, config.type, config.robots, keywordsKey, structuredDataKey])
}
