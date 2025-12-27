/**
 * API client for translation backend.
 *
 * Handles HTTP requests to the FastAPI translation service with proper
 * error handling and type safety.
 *
 * @module apiClient
 */

import type { SupportedLanguage } from './languageMetadata';

/**
 * Translation API request payload.
 */
export interface TranslateTextRequest {
  /** Text to translate (1-10000 characters) */
  text: string;
  /** Target language for translation */
  target_language: SupportedLanguage;
  /** Source language (default: 'english') */
  source_language?: SupportedLanguage;
  /** Whether to preserve technical terms in original language (default: true) */
  preserve_technical_terms?: boolean;
  /** Optional context to guide translation */
  context?: string;
}

/**
 * Translation API response payload.
 */
export interface TranslateTextResponse {
  /** Original text that was translated */
  original_text: string;
  /** Translated text */
  translated_text: string;
  /** Source language */
  source_language: SupportedLanguage;
  /** Target language */
  target_language: SupportedLanguage;
  /** Whether the target language uses right-to-left text direction */
  rtl: boolean;
}

/**
 * Custom error class for translation API errors.
 */
export class TranslationAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'TranslationAPIError';
  }
}

/**
 * Get the base URL for the translation API.
 * Checks environment variable or defaults to production URL.
 */
function getAPIBaseURL(): string {
  // Check if running in browser
  if (typeof window !== 'undefined') {
    // Check for environment variable (set in docusaurus.config.js)
    const customURL = (window as any).__TRANSLATION_API_BASE_URL__;
    if (customURL) {
      return customURL;
    }
  }

  // Default to production backend on Railway
  return 'https://physical-ai-humanoid-textbook-production.up.railway.app';
}

/**
 * Translate text using the backend translation API.
 *
 * @param request - Translation request parameters
 * @returns Promise resolving to translation response
 * @throws TranslationAPIError on API failures
 *
 * @example
 * ```ts
 * const result = await translateText({
 *   text: "Hello world",
 *   target_language: "spanish",
 * });
 * console.log(result.translated_text); // "Hola mundo"
 * ```
 */
export async function translateText(
  request: TranslateTextRequest
): Promise<TranslateTextResponse> {
  const baseURL = getAPIBaseURL();
  const endpoint = `${baseURL}/api/v1/translate/text`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Handle specific error codes
      if (response.status === 429) {
        throw new TranslationAPIError(
          'Rate limit exceeded. Please wait a moment before translating again.',
          429,
          errorData
        );
      }

      if (response.status === 422) {
        throw new TranslationAPIError(
          'Invalid request: ' + (errorData.detail || 'Please check your input.'),
          422,
          errorData
        );
      }

      if (response.status === 502 || response.status === 503) {
        throw new TranslationAPIError(
          'Translation service is temporarily unavailable. Please try again later.',
          response.status,
          errorData
        );
      }

      // Generic error
      throw new TranslationAPIError(
        `Translation failed: ${errorData.detail || response.statusText}`,
        response.status,
        errorData
      );
    }

    // Parse successful response
    const data: TranslateTextResponse = await response.json();
    return data;
  } catch (error) {
    // Re-throw TranslationAPIError as-is
    if (error instanceof TranslationAPIError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new TranslationAPIError(
        'Network error: Unable to reach translation service. Please check your connection.',
        undefined,
        error
      );
    }

    // Handle other errors
    throw new TranslationAPIError(
      'An unexpected error occurred during translation.',
      undefined,
      error
    );
  }
}

/**
 * Validate translation request before sending to API.
 *
 * @param request - Request to validate
 * @returns Validation error message or null if valid
 */
export function validateTranslationRequest(request: TranslateTextRequest): string | null {
  if (!request.text || request.text.trim().length === 0) {
    return 'Text cannot be empty.';
  }

  if (request.text.length > 10000) {
    return 'Text is too long. Maximum 10,000 characters allowed.';
  }

  if (request.text.trim().length > 1500) {
    return 'Selected text is too long. Please select up to 1,500 characters.';
  }

  if (!request.target_language) {
    return 'Target language must be specified.';
  }

  return null;
}
