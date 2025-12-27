/**
 * Floating button component for translating selected text.
 *
 * Appears near selected text and triggers translation on click.
 *
 * @module TranslateButton
 */

import React from 'react';
import styles from './TranslateButton.module.css';

export interface TranslateButtonProps {
  /** Callback when button is clicked */
  onClick: () => void;
  /** Position of the button (top, left) */
  position: { top: number; left: number };
  /** Whether translation is in progress */
  isTranslating?: boolean;
  /** Optional CSS class name */
  className?: string;
}

/**
 * TranslateButton component.
 *
 * Floating button that appears near selected text.
 * Positioned absolutely based on selection coordinates.
 *
 * @example
 * ```tsx
 * <TranslateButton
 *   onClick={handleTranslate}
 *   position={{ top: 100, left: 200 }}
 *   isTranslating={false}
 * />
 * ```
 */
export function TranslateButton({
  onClick,
  position,
  isTranslating = false,
  className,
}: TranslateButtonProps): React.ReactElement {
  return (
    <button
      className={`${styles.translateButton} ${className || ''}`.trim()}
      onClick={onClick}
      disabled={isTranslating}
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
      aria-label="Translate selected text"
      title="Translate selected text"
    >
      {isTranslating ? (
        <>
          <span className={styles.spinner} aria-hidden="true" />
          Translating...
        </>
      ) : (
        <>
          <span className={styles.icon} aria-hidden="true">
            🌐
          </span>
          Translate
        </>
      )}
    </button>
  );
}

export default TranslateButton;
