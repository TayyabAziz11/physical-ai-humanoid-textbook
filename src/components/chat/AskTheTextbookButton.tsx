import React from 'react';
import styles from './AskTheTextbookButton.module.css';

export interface AskTheTextbookButtonProps {
  onClick: () => void;
  className?: string;
}

export default function AskTheTextbookButton({ onClick, className }: AskTheTextbookButtonProps): JSX.Element {
  return (
    <button
      className={`${styles.floatingButton} ${className || ''}`}
      onClick={onClick}
      aria-label="Open textbook chat assistant"
      title="Ask the Textbook"
    >
      <span className={styles.icon}>💬</span>
      <span className={styles.label}>Ask the Textbook</span>
    </button>
  );
}
