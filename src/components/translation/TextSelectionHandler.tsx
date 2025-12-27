/**
 * Main component for handling text selection and translation.
 *
 * Detects text selection, shows translate button, manages translation state,
 * and displays results in a modal.
 *
 * @module TextSelectionHandler
 */

import React, { useState, useEffect, useCallback } from 'react';
import { LanguageSelector } from './LanguageSelector';
import { TranslateButton } from './TranslateButton';
import { TranslationModal } from './TranslationModal';
import { useTranslation, type TranslationResult } from '@site/src/hooks/useTranslation';
import {
  getSelectedText,
  validateSelection,
  getSelectionRect,
  clearSelection,
} from '@site/src/utils/selection';
import {
  DEFAULT_LANGUAGE,
  type SupportedLanguage,
} from '@site/src/utils/languageMetadata';

/**
 * Get or set the selected language from localStorage.
 */
function useStoredLanguage(): [SupportedLanguage, (lang: SupportedLanguage) => void] {
  const [language, setLanguageState] = useState<SupportedLanguage>(DEFAULT_LANGUAGE);

  useEffect(() => {
    // Load from localStorage on mount
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('translation_target_language');
      if (stored) {
        setLanguageState(stored as SupportedLanguage);
      }
    }
  }, []);

  const setLanguage = useCallback((lang: SupportedLanguage) => {
    setLanguageState(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('translation_target_language', lang);
    }
  }, []);

  return [language, setLanguage];
}

/**
 * TextSelectionHandler component.
 *
 * Global component that handles text selection translation throughout the site.
 * Should be rendered once at the root level (e.g., in Docusaurus Root theme).
 *
 * @example
 * ```tsx
 * // In src/theme/Root.tsx
 * export default function Root({ children }) {
 *   return (
 *     <>
 *       {children}
 *       <TextSelectionHandler />
 *     </>
 *   );
 * }
 * ```
 */
export function TextSelectionHandler(): React.ReactElement | null {
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [buttonPosition, setButtonPosition] = useState<{ top: number; left: number } | null>(
    null
  );
  const [targetLanguage, setTargetLanguage] = useStoredLanguage();
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [translationResult, setTranslationResult] = useState<TranslationResult | null>(null);

  const { translate, isTranslating, error } = useTranslation();

  /**
   * Handle text selection events.
   */
  const handleSelection = useCallback(() => {
    const text = getSelectedText();

    // Hide button if no selection
    if (!text) {
      setSelectedText(null);
      setButtonPosition(null);
      setShowLanguageSelector(false);
      return;
    }

    // Validate selection
    const validation = validateSelection(text);
    if (!validation.valid) {
      setSelectedText(null);
      setButtonPosition(null);
      setShowLanguageSelector(false);
      return;
    }

    // Get selection position
    const rect = getSelectionRect();
    if (!rect) return;

    // Calculate button position (above selection, centered)
    const top = rect.top + window.scrollY - 45; // 45px above selection
    const left = rect.left + rect.width / 2 - 60; // Center horizontally (button is ~120px wide)

    setSelectedText(text);
    setButtonPosition({ top, left });
    setShowLanguageSelector(true);
  }, []);

  /**
   * Set up event listeners for selection detection.
   */
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Debounce to avoid excessive updates
    let timeoutId: NodeJS.Timeout;

    const debouncedHandler = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleSelection, 100);
    };

    document.addEventListener('mouseup', debouncedHandler);
    document.addEventListener('keyup', debouncedHandler);
    document.addEventListener('selectionchange', debouncedHandler);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('mouseup', debouncedHandler);
      document.removeEventListener('keyup', debouncedHandler);
      document.removeEventListener('selectionchange', debouncedHandler);
    };
  }, [handleSelection]);

  /**
   * Handle translate button click.
   */
  const handleTranslate = useCallback(async () => {
    if (!selectedText) return;

    const result = await translate(selectedText, targetLanguage);

    if (result) {
      setTranslationResult(result);
      setSelectedText(null);
      setButtonPosition(null);
      setShowLanguageSelector(false);
      clearSelection();
    }
  }, [selectedText, targetLanguage, translate]);

  /**
   * Handle modal close.
   */
  const handleModalClose = useCallback(() => {
    setTranslationResult(null);
  }, []);

  /**
   * Handle clicks outside the language selector/button to close it.
   */
  useEffect(() => {
    if (!showLanguageSelector) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;

      // Don't close if clicking on the button or language selector
      if (
        target.closest('[data-translate-button]') ||
        target.closest('[data-language-selector]')
      ) {
        return;
      }

      // Close if clicking elsewhere
      setSelectedText(null);
      setButtonPosition(null);
      setShowLanguageSelector(false);
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showLanguageSelector]);

  return (
    <>
      {/* Language selector and translate button (shown when text is selected) */}
      {showLanguageSelector && buttonPosition && selectedText && (
        <div
          style={{
            position: 'fixed',
            top: `${buttonPosition.top - 50}px`,
            left: `${buttonPosition.left - 100}px`,
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            padding: '0.75rem',
            backgroundColor: 'var(--ifm-background-color)',
            border: '1px solid var(--ifm-color-emphasis-300)',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          }}
          data-language-selector
        >
          <LanguageSelector
            currentLanguage={targetLanguage}
            onLanguageChange={setTargetLanguage}
            showLabel={true}
            label="Translate to:"
          />
          <TranslateButton
            onClick={handleTranslate}
            position={buttonPosition}
            isTranslating={isTranslating}
          />
        </div>
      )}

      {/* Error display */}
      {error && (
        <div
          style={{
            position: 'fixed',
            bottom: '1rem',
            right: '1rem',
            padding: '1rem',
            backgroundColor: 'var(--ifm-color-danger-lightest)',
            color: 'var(--ifm-color-danger-darkest)',
            border: '1px solid var(--ifm-color-danger-light)',
            borderRadius: '0.375rem',
            maxWidth: '400px',
            zIndex: 9998,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          }}
        >
          <strong>Translation Error:</strong> {error}
        </div>
      )}

      {/* Translation result modal */}
      {translationResult && (
        <TranslationModal result={translationResult} onClose={handleModalClose} />
      )}
    </>
  );
}

export default TextSelectionHandler;
