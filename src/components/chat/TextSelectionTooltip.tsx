import React from 'react';
import styles from './TextSelectionTooltip.module.css';

export interface TextSelectionTooltipProps {
  isVisible: boolean;
  position: { x: number; y: number };
  onAskAboutSelection: () => void;
  className?: string;
}

export default function TextSelectionTooltip({
  isVisible,
  position,
  onAskAboutSelection,
  className
}: TextSelectionTooltipProps): JSX.Element {
  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`${styles.tooltip} ${className || ''}`}
      style={{
        top: `${position.y}px`,
        left: `${position.x}px`,
      }}
    >
      <button
        className={styles.button}
        onClick={onAskAboutSelection}
        aria-label="Ask about selected text"
      >
        <span className={styles.icon}>💡</span>
        <span className={styles.label}>Ask about this</span>
      </button>
    </div>
  );
}
