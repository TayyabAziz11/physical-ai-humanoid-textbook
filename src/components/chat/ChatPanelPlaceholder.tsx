import React, { useState } from 'react';
import styles from './ChatPanelPlaceholder.module.css';

export interface ChatPanelPlaceholderProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

type ChatMode = 'whole-book' | 'selection';

export default function ChatPanelPlaceholder({ isOpen, onClose, className }: ChatPanelPlaceholderProps): JSX.Element {
  const [mode, setMode] = useState<ChatMode>('whole-book');

  if (!isOpen) {
    return null;
  }

  return (
    <div className={`${styles.overlay} ${className || ''}`} onClick={onClose}>
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title}>Study Assistant</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close chat panel"
          >
            ✕
          </button>
        </div>

        {/* Mode selector */}
        <div className={styles.modeSelector}>
          <button
            className={`${styles.modeButton} ${mode === 'whole-book' ? styles.active : ''}`}
            onClick={() => setMode('whole-book')}
            aria-pressed={mode === 'whole-book'}
          >
            📚 Whole-book Q&A
          </button>
          <button
            className={`${styles.modeButton} ${mode === 'selection' ? styles.active : ''}`}
            onClick={() => setMode('selection')}
            aria-pressed={mode === 'selection'}
          >
            🔍 Selection-based Q&A
          </button>
        </div>

        {/* Placeholder content */}
        <div className={styles.content}>
          <div className={styles.placeholderMessage}>
            <div className={styles.iconLarge}>🚧</div>
            <h3 className={styles.placeholderTitle}>Coming Soon</h3>
            <p className={styles.placeholderText}>
              {mode === 'whole-book'
                ? 'Chatbot backend not connected yet. Soon you\'ll be able to ask questions about any topic in the entire textbook.'
                : 'Chatbot backend not connected yet. Soon you\'ll be able to select text and ask specific questions about it.'
              }
            </p>
            <div className={styles.featureList}>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>✨</span>
                <span>AI-powered answers from textbook content</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🎯</span>
                <span>Context-aware explanations</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>📖</span>
                <span>References to source chapters</span>
              </div>
            </div>
          </div>
        </div>

        {/* Input area (disabled) */}
        <div className={styles.inputArea}>
          <input
            type="text"
            className={styles.input}
            placeholder="Ask a question..."
            disabled
            aria-label="Chat input (currently disabled)"
          />
          <button className={styles.sendButton} disabled aria-label="Send message (currently disabled)">
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
