/**
 * Language selector dropdown component for multilingual translation.
 *
 * Allows users to select their preferred target language for translations.
 * Shows all supported languages with native names and flag emojis.
 *
 * @module LanguageSelector
 */

import React from 'react';
import { SUPPORTED_LANGUAGES, type SupportedLanguage } from '@site/src/utils/languageMetadata';
import styles from './LanguageSelector.module.css';

export interface LanguageSelectorProps {
  /** Currently selected language code */
  currentLanguage: SupportedLanguage;
  /** Callback when language selection changes */
  onLanguageChange: (language: SupportedLanguage) => void;
  /** Optional CSS class name for custom styling */
  className?: string;
  /** Optional label text (default: "Translate to:") */
  label?: string;
  /** Whether to show the label (default: true) */
  showLabel?: boolean;
}

/**
 * LanguageSelector component.
 *
 * Renders a dropdown with all supported languages, displaying both
 * English names and native names for better accessibility.
 *
 * @example
 * ```tsx
 * <LanguageSelector
 *   currentLanguage={selectedLanguage}
 *   onLanguageChange={setSelectedLanguage}
 * />
 * ```
 */
export function LanguageSelector({
  currentLanguage,
  onLanguageChange,
  className,
  label = 'Translate to:',
  showLabel = true,
}: LanguageSelectorProps): React.ReactElement {
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = event.target.value as SupportedLanguage;
    onLanguageChange(newLanguage);
  };

  return (
    <div className={`${styles.languageSelector} ${className || ''}`.trim()}>
      {showLabel && (
        <label htmlFor="language-select" className={styles.label}>
          {label}
        </label>
      )}
      <select
        id="language-select"
        className={styles.select}
        value={currentLanguage}
        onChange={handleChange}
        aria-label="Select target language for translation"
      >
        {SUPPORTED_LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name} ({lang.nativeName})
          </option>
        ))}
      </select>
    </div>
  );
}

export default LanguageSelector;
