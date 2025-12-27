/**
 * React hook for managing translation cache in localStorage.
 *
 * Implements client-side caching with TTL (time-to-live) and LRU eviction
 * to reduce redundant API calls and improve user experience.
 *
 * @module useTranslationCache
 */

import { useCallback } from 'react';
import type { SupportedLanguage } from '@site/src/utils/languageMetadata';

/**
 * Cache entry structure.
 */
export interface CacheEntry {
  /** Original text */
  originalText: string;
  /** Translated text */
  translatedText: string;
  /** Target language */
  targetLanguage: SupportedLanguage;
  /** Source language */
  sourceLanguage: SupportedLanguage;
  /** Timestamp when cached (milliseconds since epoch) */
  timestamp: number;
  /** Whether target language is RTL */
  rtl: boolean;
}

/**
 * Cache configuration.
 */
const CACHE_CONFIG = {
  /** Cache time-to-live: 7 days */
  TTL_MS: 7 * 24 * 60 * 60 * 1000,
  /** Maximum entries per language */
  MAX_ENTRIES_PER_LANGUAGE: 50,
  /** localStorage key prefix */
  STORAGE_KEY_PREFIX: 'translation_cache_',
} as const;

/**
 * Generate cache key for a text + language combination.
 * Uses a simple hash to keep keys short.
 */
function generateCacheKey(text: string, targetLanguage: SupportedLanguage): string {
  // Simple hash function (djb2)
  let hash = 5381;
  for (let i = 0; i < text.length; i++) {
    hash = (hash * 33) ^ text.charCodeAt(i);
  }
  return `${CACHE_CONFIG.STORAGE_KEY_PREFIX}${targetLanguage}_${hash >>> 0}`;
}

/**
 * Get all cache entries for a specific language from localStorage.
 */
function getLanguageCacheEntries(targetLanguage: SupportedLanguage): CacheEntry[] {
  if (typeof window === 'undefined') return [];

  const entries: CacheEntry[] = [];
  const prefix = `${CACHE_CONFIG.STORAGE_KEY_PREFIX}${targetLanguage}_`;

  // Scan localStorage for matching keys
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith(prefix)) {
      try {
        const value = localStorage.getItem(key);
        if (value) {
          const entry = JSON.parse(value) as CacheEntry;
          entries.push(entry);
        }
      } catch {
        // Invalid entry, skip
      }
    }
  }

  return entries;
}

/**
 * Evict old entries if cache size exceeds limit.
 * Uses LRU (Least Recently Used) eviction strategy.
 */
function evictOldEntries(targetLanguage: SupportedLanguage): void {
  const entries = getLanguageCacheEntries(targetLanguage);

  if (entries.length <= CACHE_CONFIG.MAX_ENTRIES_PER_LANGUAGE) {
    return;
  }

  // Sort by timestamp (oldest first)
  entries.sort((a, b) => a.timestamp - b.timestamp);

  // Calculate how many to remove
  const removeCount = entries.length - CACHE_CONFIG.MAX_ENTRIES_PER_LANGUAGE;

  // Remove oldest entries
  for (let i = 0; i < removeCount; i++) {
    const entry = entries[i];
    const key = generateCacheKey(entry.originalText, targetLanguage);
    localStorage.removeItem(key);
  }
}

/**
 * Hook for managing translation cache.
 *
 * @returns Cache management functions
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { get, set, clear } = useTranslationCache();
 *
 *   const cached = get("Hello world", "spanish");
 *   if (cached) {
 *     return <div>{cached.translatedText}</div>;
 *   }
 *
 *   // ... fetch translation ...
 *   set("Hello world", "spanish", result);
 * }
 * ```
 */
export function useTranslationCache() {
  /**
   * Get cached translation.
   *
   * @param text - Original text
   * @param targetLanguage - Target language
   * @returns Cached entry or null if not found/expired
   */
  const get = useCallback(
    (text: string, targetLanguage: SupportedLanguage): CacheEntry | null => {
      if (typeof window === 'undefined') return null;

      const key = generateCacheKey(text, targetLanguage);
      const value = localStorage.getItem(key);

      if (!value) return null;

      try {
        const entry = JSON.parse(value) as CacheEntry;

        // Check if expired
        const now = Date.now();
        if (now - entry.timestamp > CACHE_CONFIG.TTL_MS) {
          localStorage.removeItem(key);
          return null;
        }

        return entry;
      } catch {
        // Invalid entry, remove it
        localStorage.removeItem(key);
        return null;
      }
    },
    []
  );

  /**
   * Store translation in cache.
   *
   * @param text - Original text
   * @param targetLanguage - Target language
   * @param translatedText - Translated text
   * @param sourceLanguage - Source language
   * @param rtl - Whether target language is RTL
   */
  const set = useCallback(
    (
      text: string,
      targetLanguage: SupportedLanguage,
      translatedText: string,
      sourceLanguage: SupportedLanguage,
      rtl: boolean
    ): void => {
      if (typeof window === 'undefined') return;

      const entry: CacheEntry = {
        originalText: text,
        translatedText,
        targetLanguage,
        sourceLanguage,
        timestamp: Date.now(),
        rtl,
      };

      const key = generateCacheKey(text, targetLanguage);

      try {
        localStorage.setItem(key, JSON.stringify(entry));

        // Evict old entries if needed
        evictOldEntries(targetLanguage);
      } catch (error) {
        // localStorage full or disabled, fail silently
        console.warn('Failed to cache translation:', error);
      }
    },
    []
  );

  /**
   * Clear all cached translations for a specific language.
   *
   * @param targetLanguage - Language to clear cache for (optional, clears all if not specified)
   */
  const clear = useCallback((targetLanguage?: SupportedLanguage): void => {
    if (typeof window === 'undefined') return;

    if (targetLanguage) {
      // Clear specific language
      const entries = getLanguageCacheEntries(targetLanguage);
      entries.forEach(entry => {
        const key = generateCacheKey(entry.originalText, targetLanguage);
        localStorage.removeItem(key);
      });
    } else {
      // Clear all translation cache entries
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(CACHE_CONFIG.STORAGE_KEY_PREFIX)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));
    }
  }, []);

  /**
   * Get cache statistics.
   *
   * @returns Cache stats by language
   */
  const getStats = useCallback((): Record<SupportedLanguage, number> => {
    if (typeof window === 'undefined') {
      return {} as Record<SupportedLanguage, number>;
    }

    const stats: Partial<Record<SupportedLanguage, number>> = {};

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(CACHE_CONFIG.STORAGE_KEY_PREFIX)) {
        const lang = key.split('_')[2] as SupportedLanguage;
        stats[lang] = (stats[lang] || 0) + 1;
      }
    }

    return stats as Record<SupportedLanguage, number>;
  }, []);

  return { get, set, clear, getStats };
}

export default useTranslationCache;
