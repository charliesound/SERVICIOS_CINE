export interface SeoConfig {
  title: string
  description: string
  path?: string
  image?: string
  type?: string
  robots?: string
  keywords?: string[]
  structuredData?: Record<string, unknown> | Array<Record<string, unknown>>
}

const ABSOLUTE_URL_PATTERN = /^https?:\/\//i
const STRUCTURED_DATA_SCRIPT_ID = 'app-seo-structured-data'

export const SEO_SITE_NAME = 'AILinkCinema'
export const SEO_DEFAULT_TITLE = 'AILinkCinema | IA para cine y produccion audiovisual'
export const SEO_DEFAULT_DESCRIPTION =
  'Software y soluciones de inteligencia artificial para cine, television y publicidad: guion, storyboard, produccion, doblaje, postproduccion y delivery.'
export const SEO_DEFAULT_IMAGE_PATH = '/assets/cid-storyboard-1.png'

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, '')
}

function ensureMetaByName(name: string) {
  let meta = document.head.querySelector(`meta[name="${name}"]`) as HTMLMetaElement | null
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute('name', name)
    document.head.appendChild(meta)
  }
  return meta
}

function ensureMetaByProperty(property: string) {
  let meta = document.head.querySelector(`meta[property="${property}"]`) as HTMLMetaElement | null
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute('property', property)
    document.head.appendChild(meta)
  }
  return meta
}

function ensureLink(rel: string) {
  let link = document.head.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', rel)
    document.head.appendChild(link)
  }
  return link
}

function removeMetaByName(name: string) {
  document.head.querySelector(`meta[name="${name}"]`)?.remove()
}

export function getSiteOrigin() {
  const configuredOrigin = import.meta.env.VITE_SITE_URL?.trim()
  if (configuredOrigin) {
    return trimTrailingSlash(configuredOrigin)
  }
  if (typeof window !== 'undefined') {
    return trimTrailingSlash(window.location.origin)
  }
  return ''
}

export function buildAbsoluteUrl(path: string) {
  if (ABSOLUTE_URL_PATTERN.test(path)) {
    return path
  }

  const siteOrigin = getSiteOrigin()
  if (!siteOrigin) {
    return path
  }

  return `${siteOrigin}${path.startsWith('/') ? path : `/${path}`}`
}

export function buildBreadcrumbStructuredData(items: Array<{ name: string; path: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: buildAbsoluteUrl(item.path),
    })),
  }
}

export function applySeo({
  title,
  description,
  path,
  image = SEO_DEFAULT_IMAGE_PATH,
  type = 'website',
  robots,
  keywords,
  structuredData,
}: SeoConfig) {
  const pagePath = path || (typeof window !== 'undefined' ? `${window.location.pathname}${window.location.search}` : '/')
  const canonicalUrl = buildAbsoluteUrl(pagePath)
  const imageUrl = buildAbsoluteUrl(image)
  const fullTitle = title.includes(SEO_SITE_NAME) ? title : `${title} | ${SEO_SITE_NAME}`

  document.documentElement.lang = 'es'
  document.title = fullTitle

  ensureMetaByName('description').setAttribute('content', description)
  ensureMetaByName('twitter:card').setAttribute('content', 'summary_large_image')
  ensureMetaByName('twitter:title').setAttribute('content', fullTitle)
  ensureMetaByName('twitter:description').setAttribute('content', description)
  ensureMetaByName('twitter:image').setAttribute('content', imageUrl)

  if (robots) {
    ensureMetaByName('robots').setAttribute('content', robots)
  } else {
    removeMetaByName('robots')
  }

  if (keywords && keywords.length > 0) {
    ensureMetaByName('keywords').setAttribute('content', keywords.join(', '))
  } else {
    removeMetaByName('keywords')
  }

  ensureMetaByProperty('og:locale').setAttribute('content', 'es_ES')
  ensureMetaByProperty('og:site_name').setAttribute('content', SEO_SITE_NAME)
  ensureMetaByProperty('og:type').setAttribute('content', type)
  ensureMetaByProperty('og:title').setAttribute('content', fullTitle)
  ensureMetaByProperty('og:description').setAttribute('content', description)
  ensureMetaByProperty('og:url').setAttribute('content', canonicalUrl)
  ensureMetaByProperty('og:image').setAttribute('content', imageUrl)

  ensureLink('canonical').setAttribute('href', canonicalUrl)

  document.getElementById(STRUCTURED_DATA_SCRIPT_ID)?.remove()
  if (structuredData) {
    const script = document.createElement('script')
    script.id = STRUCTURED_DATA_SCRIPT_ID
    script.type = 'application/ld+json'
    script.textContent = JSON.stringify(structuredData)
    document.head.appendChild(script)
  }
}
