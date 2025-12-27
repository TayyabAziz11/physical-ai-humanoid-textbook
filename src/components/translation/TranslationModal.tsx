/**
 * Modal component for displaying translation results.
 *
 * Shows original and translated text side-by-side with proper RTL support
 * for Arabic and Urdu. Includes copy-to-clipboard and display options.
 *
 * @module TranslationModal
 */

import React, { useState, useCallback } from 'react';
import { getTextDirection, getLanguageInfo } from '@site/src/utils/languageMetadata';
import type { TranslationResult } from '@site/src/hooks/useTranslation';
import styles from './TranslationModal.module.css';

export interface TranslationModalProps {
  /** Translation result to display */
  result: TranslationResult;
  /** Callback when modal is closed */
  onClose: () => void;
  /** Whether to show the original text section (default: true) */
  showOriginal?: boolean;
}

/**
 * TranslationModal component.
 *
 * Displays translation results in a modal overlay with:
 * - Original text (optional)
 * - Translated text with proper RTL support
 * - Language metadata
 * - Copy to clipboard functionality
 * - Cache status indicator
 *
 * @example
 * ```tsx
 * {showModal && (
 *   <TranslationModal
 *     result={translationResult}
 *     onClose={() => setShowModal(false)}
 *   />
 * )}
 * ```
 */
export function TranslationModal({
  result,
  onClose,
  showOriginal = true,
}: TranslationModalProps): React.ReactElement {
  const [copied, setCopied] = useState(false);
  const [showOriginalText, setShowOriginalText] = useState(showOriginal);

  const targetLanguage = getLanguageInfo(result.target_language);
  const sourceLanguage = getLanguageInfo(result.source_language);

  /**
   * Copy translated text to clipboard.
   */
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(result.translated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  }, [result.translated_text]);

  /**
   * Handle backdrop click to close modal.
   */
  const handleBackdropClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (event.target === event.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  /**
   * Handle escape key to close modal.
   */
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  return (
    <div
      className={styles.backdrop}
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="translation-modal-title"
    >
      <div className={styles.modal}>
        {/* Header */}
        <div className={styles.header}>
          <h2 id="translation-modal-title" className={styles.title}>
            Translation
            {result.fromCache && (
              <span className={styles.cacheBadge} title="Loaded from cache">
                ⚡ Cached
              </span>
            )}
          </h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close translation modal"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {/* Language Info */}
          <div className={styles.languageInfo}>
            <span>
              {sourceLanguage?.flag} {sourceLanguage?.name}
            </span>
            <span className={styles.arrow}>→</span>
            <span>
              {targetLanguage?.flag} {targetLanguage?.nativeName}
            </span>
          </div>

          {/* Original Text (Optional) */}
          {showOriginalText && (
            <div className={styles.textSection}>
              <div className={styles.sectionHeader}>
                <h3 className={styles.sectionTitle}>Original</h3>
                <button
                  className={styles.toggleButton}
                  onClick={() => setShowOriginalText(false)}
                  aria-label="Hide original text"
                >
                  Hide
                </button>
              </div>
              <div
                className={styles.textContent}
                dir={getTextDirection(result.source_language)}
              >
                {result.original_text}
              </div>
            </div>
          )}

          {!showOriginalText && showOriginal && (
            <button
              className={styles.showOriginalButton}
              onClick={() => setShowOriginalText(true)}
            >
              Show Original Text
            </button>
          )}

          {/* Translated Text */}
          <div className={styles.textSection}>
            <div className={styles.sectionHeader}>
              <h3 className={styles.sectionTitle}>
                Translation
                {result.rtl && (
                  <span className={styles.rtlBadge} title="Right-to-left language">
                    RTL
                  </span>
                )}
              </h3>
              <button
                className={styles.copyButton}
                onClick={handleCopy}
                disabled={copied}
                aria-label="Copy translated text to clipboard"
              >
                {copied ? '✓ Copied!' : '📋 Copy'}
              </button>
            </div>
            <div
              className={`${styles.textContent} ${styles.translatedText}`}
              dir={getTextDirection(result.target_language)}
            >
              {result.translated_text}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button className={styles.closeFooterButton} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default TranslationModal;
