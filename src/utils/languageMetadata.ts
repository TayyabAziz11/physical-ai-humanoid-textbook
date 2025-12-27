/**
 * Language metadata for multilingual translation feature.
 *
 * Defines supported languages with native names and RTL (right-to-left) flags
 * to enable proper text rendering for Arabic and Urdu.
 *
 * @module languageMetadata
 */

/**
 * Supported language codes.
 * Must match backend SupportedLanguage type.
 */
export type SupportedLanguage =
  | 'english'
  | 'urdu'
  | 'mandarin'
  | 'japanese'
  | 'spanish'
  | 'french'
  | 'arabic';

/**
 * Language metadata interface.
 */
export interface LanguageInfo {
  /** Language code (lowercase, matches backend) */
  code: SupportedLanguage;
  /** English name */
  name: string;
  /** Native name (in the language's script) */
  nativeName: string;
  /** Whether the language uses right-to-left text direction */
  rtl: boolean;
  /** Emoji flag for visual identification */
  flag: string;
}

/**
 * Complete language metadata for all supported languages.
 * Ordered by expected usage frequency.
 */
export const SUPPORTED_LANGUAGES: readonly LanguageInfo[] = [
  {
    code: 'english',
    name: 'English',
    nativeName: 'English',
    rtl: false,
    flag: '🇬🇧',
  },
  {
    code: 'urdu',
    name: 'Urdu',
    nativeName: 'اردو',
    rtl: true,
    flag: '🇵🇰',
  },
  {
    code: 'arabic',
    name: 'Arabic',
    nativeName: 'العربية',
    rtl: true,
    flag: '🇸🇦',
  },
  {
    code: 'spanish',
    name: 'Spanish',
    nativeName: 'Español',
    rtl: false,
    flag: '🇪🇸',
  },
  {
    code: 'mandarin',
    name: 'Mandarin Chinese',
    nativeName: '中文',
    rtl: false,
    flag: '🇨🇳',
  },
  {
    code: 'japanese',
    name: 'Japanese',
    nativeName: '日本語',
    rtl: false,
    flag: '🇯🇵',
  },
  {
    code: 'french',
    name: 'French',
    nativeName: 'Français',
    rtl: false,
    flag: '🇫🇷',
  },
] as const;

/**
 * Map of language codes to their metadata for O(1) lookup.
 */
export const LANGUAGE_MAP: ReadonlyMap<SupportedLanguage, LanguageInfo> = new Map(
  SUPPORTED_LANGUAGES.map(lang => [lang.code, lang])
);

/**
 * Get language metadata by code.
 *
 * @param code - Language code
 * @returns Language metadata or undefined if not found
 *
 * @example
 * ```ts
 * const arabic = getLanguageInfo('arabic');
 * console.log(arabic?.rtl); // true
 * console.log(arabic?.nativeName); // "العربية"
 * ```
 */
export function getLanguageInfo(code: SupportedLanguage): LanguageInfo | undefined {
  return LANGUAGE_MAP.get(code);
}

/**
 * Check if a language uses right-to-left text direction.
 *
 * @param code - Language code
 * @returns True if the language is RTL, false otherwise
 *
 * @example
 * ```ts
 * isRTL('arabic'); // true
 * isRTL('urdu'); // true
 * isRTL('spanish'); // false
 * ```
 */
export function isRTL(code: SupportedLanguage): boolean {
  return LANGUAGE_MAP.get(code)?.rtl ?? false;
}

/**
 * Get the text direction attribute value for a language.
 *
 * @param code - Language code
 * @returns 'rtl' or 'ltr'
 *
 * @example
 * ```tsx
 * <div dir={getTextDirection('arabic')}>
 *   {translatedText}
 * </div>
 * ```
 */
export function getTextDirection(code: SupportedLanguage): 'rtl' | 'ltr' {
  return isRTL(code) ? 'rtl' : 'ltr';
}

/**
 * Validate if a string is a supported language code.
 *
 * @param code - String to validate
 * @returns True if the code is a valid SupportedLanguage
 *
 * @example
 * ```ts
 * isValidLanguageCode('spanish'); // true
 * isValidLanguageCode('german'); // false
 * ```
 */
export function isValidLanguageCode(code: string): code is SupportedLanguage {
  return LANGUAGE_MAP.has(code as SupportedLanguage);
}

/**
 * Default language code.
 */
export const DEFAULT_LANGUAGE: SupportedLanguage = 'english';
