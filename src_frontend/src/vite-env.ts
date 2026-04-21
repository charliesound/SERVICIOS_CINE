export function getThumbnailUrl(filename: string): string {
  const baseUrl = import.meta.env.VITE_COMFY_URL || 'http://localhost:8188'
  if (!filename) return ''
  return `${baseUrl}/view?filename=${encodeURIComponent(filename)}`
}

export function isComfyAsset(assetSource: string | null | undefined): boolean {
  return assetSource === 'comfyui'
}
