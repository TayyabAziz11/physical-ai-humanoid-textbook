import React, { useState } from 'react';
import styles from './ChapterActionsBar.module.css';

export interface ChapterActionsBarProps {
  className?: string;
}

export default function ChapterActionsBar({ className }: ChapterActionsBarProps): JSX.Element {
  const [showPersonalizeBanner, setShowPersonalizeBanner] = useState(false);
  const [showUrduBanner, setShowUrduBanner] = useState(false);

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={styles.buttonGroup}>
        <button
          className={styles.actionButton}
          onClick={() => {
            setShowPersonalizeBanner(true);
            setShowUrduBanner(false);
          }}
          aria-label="Personalize chapter content"
        >
          ✨ Personalize for Me
        </button>
        <button
          className={styles.actionButton}
          onClick={() => {
            setShowUrduBanner(true);
            setShowPersonalizeBanner(false);
          }}
          aria-label="View chapter in Urdu"
        >
          🌐 View in Urdu
        </button>
      </div>

      {showPersonalizeBanner && (
        <div className={styles.banner} role="alert">
          <span className={styles.bannerIcon}>ℹ️</span>
          <span className={styles.bannerText}>
            Personalization coming soon – AI will adapt this chapter to your learning style and background
          </span>
          <button
            className={styles.closeBanner}
            onClick={() => setShowPersonalizeBanner(false)}
            aria-label="Close banner"
          >
            ✕
          </button>
        </div>
      )}

      {showUrduBanner && (
        <div className={styles.banner} role="alert">
          <span className={styles.bannerIcon}>ℹ️</span>
          <span className={styles.bannerText}>
            Urdu translation coming soon – Full textbook will be available in اردو
          </span>
          <button
            className={styles.closeBanner}
            onClick={() => setShowUrduBanner(false)}
            aria-label="Close banner"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
