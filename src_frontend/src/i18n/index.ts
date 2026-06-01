import { useSyncExternalStore } from 'react'
import en from './en.json'
import es from './es.json'

type Language = 'es' | 'en'
interface MessageTree {
  [key: string]: string | MessageTree
}

const STORAGE_KEY = 'cid_language'
const messages: Record<Language, MessageTree> = { es, en }
const listeners = new Set<() => void>()

function normalizeLanguage(value: string | null | undefined): Language {
  return value === 'en' ? 'en' : 'es'
}

function readStoredLanguage(): Language {
  if (typeof window === 'undefined') return 'es'
  return normalizeLanguage(window.localStorage.getItem(STORAGE_KEY))
}

let currentLanguage: Language = readStoredLanguage()

function emitChange() {
  listeners.forEach((listener) => listener())
}

function resolveMessage(language: Language, key: string): string | undefined {
  const parts = key.split('.')
  let current: string | MessageTree | undefined = messages[language]

  for (const part of parts) {
    if (!current || typeof current === 'string') return undefined
    current = current[part]
  }

  return typeof current === 'string' ? current : undefined
}

export function getLanguage(): Language {
  return currentLanguage
}

export function setLanguage(language: string): Language {
  const normalized = normalizeLanguage(language)
  if (normalized === currentLanguage) return currentLanguage

  currentLanguage = normalized
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, normalized)
  }
  emitChange()
  return currentLanguage
}

export function t(key: string): string {
  return resolveMessage(currentLanguage, key) ?? resolveMessage('es', key) ?? key
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useLanguage() {
  const language = useSyncExternalStore(subscribe, getLanguage, () => 'es')
  return {
    language,
    setLanguage,
    t,
  }
}

export const i18nStorageKey = STORAGE_KEY
