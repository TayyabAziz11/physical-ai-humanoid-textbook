/**
 * React hook for translating text with caching and state management.
 *
 * Orchestrates API calls, caching, error handling, and loading states
 * for the translation feature.
 *
 * @module useTranslation
 */

import { useState, useCallback } from 'react';
import {
  translateText,
  validateTranslationRequest,
  TranslationAPIError,
  type TranslateTextRequest,
  type TranslateTextResponse,
} from '@site/src/utils/apiClient';
import { useTranslationCache } from './useTranslationCache';
import type { SupportedLanguage } from '@site/src/utils/languageMetadata';

/**
 * Translation result with cache metadata.
 */
export interface TranslationResult extends TranslateTextResponse {
  /** Whether this result came from cache */
  fromCache: boolean;
}

/**
 * Translation options.
 */
export interface TranslationOptions {
  /** Source language (default: 'english') */
  sourceLanguage?: SupportedLanguage;
  /** Whether to preserve technical terms (default: true) */
  preserveTechnicalTerms?: boolean;
  /** Optional context to guide translation */
  context?: string;
  /** Whether to bypass cache and force API call (default: false) */
  bypassCache?: boolean;
}

/**
 * Hook for translating text.
 *
 * @returns Translation functions and state
 *
 * @example
 * ```tsx
 * function TranslateButton() {
 *   const { translate, isTranslating, error } = useTranslation();
 *
 *   const handleClick = async () => {
 *     const result = await translate("Hello world", "spanish");
 *     if (result) {
 *       console.log(result.translated_text);
 *       console.log("From cache:", result.fromCache);
 *     }
 *   };
 *
 *   return (
 *     <button onClick={handleClick} disabled={isTranslating}>
 *       {isTranslating ? "Translating..." : "Translate"}
 *     </button>
 *   );
 * }
 * ```
 */
export function useTranslation() {
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cache = useTranslationCache();

  /**
   * Translate text to target language.
   *
   * Checks cache first, falls back to API if not found.
   * Updates cache with successful API responses.
   *
   * @param text - Text to translate
   * @param targetLanguage - Target language
   * @param options - Translation options
   * @returns Translation result or null on error
   */
  const translate = useCallback(
    async (
      text: string,
      targetLanguage: SupportedLanguage,
      options: TranslationOptions = {}
    ): Promise<TranslationResult | null> => {
      const {
        sourceLanguage = 'english',
        preserveTechnicalTerms = true,
        context,
        bypassCache = false,
      } = options;

      // Reset error state
      setError(null);

      // Validate request
      const request: TranslateTextRequest = {
        text,
        target_language: targetLanguage,
        source_language: sourceLanguage,
        preserve_technical_terms: preserveTechnicalTerms,
        context,
      };

      const validationError = validateTranslationRequest(request);
      if (validationError) {
        setError(validationError);
        return null;
      }

      // Check cache (unless bypassed)
      if (!bypassCache) {
        const cached = cache.get(text, targetLanguage);
        if (cached) {
          return {
            original_text: cached.originalText,
            translated_text: cached.translatedText,
            source_language: cached.sourceLanguage,
            target_language: cached.targetLanguage,
            rtl: cached.rtl,
            fromCache: true,
          };
        }
      }

      // Call API
      setIsTranslating(true);

      try {
        const response = await translateText(request);

        // Cache the result
        cache.set(
          response.original_text,
          response.target_language,
          response.translated_text,
          response.source_language,
          response.rtl
        );

        return {
          ...response,
          fromCache: false,
        };
      } catch (err) {
        // Handle errors
        if (err instanceof TranslationAPIError) {
          setError(err.message);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unexpected error occurred during translation.');
        }
        return null;
      } finally {
        setIsTranslating(false);
      }
    },
    [cache]
  );

  /**
   * Clear error state.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Clear translation cache.
   *
   * @param targetLanguage - Language to clear (optional, clears all if not specified)
   */
  const clearCache = useCallback(
    (targetLanguage?: SupportedLanguage) => {
      cache.clear(targetLanguage);
    },
    [cache]
  );

  return {
    /** Translate text function */
    translate,
    /** Whether a translation is currently in progress */
    isTranslating,
    /** Current error message (null if no error) */
    error,
    /** Clear the current error */
    clearError,
    /** Clear translation cache */
    clearCache,
    /** Get cache statistics */
    getCacheStats: cache.getStats,
  };
}

export default useTranslation;
