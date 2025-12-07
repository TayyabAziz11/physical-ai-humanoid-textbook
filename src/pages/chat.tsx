import React, { useState } from 'react';
import Layout from '@theme/Layout';
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';
import styles from './chat.module.css';

export default function ChatPage(): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(true);

  return (
    <Layout
      title="Study Assistant"
      description="Interactive AI study assistant for the Physical AI & Humanoid Robotics Textbook"
    >
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Study Assistant</h1>
          <p className={styles.subtitle}>
            Your AI-powered companion for learning Physical AI and Humanoid Robotics
          </p>
        </div>

        <div className={styles.infoSection}>
          <div className={styles.infoCard}>
            <div className={styles.infoIcon}>📚</div>
            <h2 className={styles.infoTitle}>Whole-book Q&A</h2>
            <p className={styles.infoText}>
              Ask questions about any topic across the entire textbook. Get comprehensive answers
              with references to relevant chapters.
            </p>
          </div>

          <div className={styles.infoCard}>
            <div className={styles.infoIcon}>🔍</div>
            <h2 className={styles.infoTitle}>Selection-based Q&A</h2>
            <p className={styles.infoText}>
              Select specific text in any chapter and ask targeted questions. Get context-aware
              explanations focused on your selection.
            </p>
          </div>

          <div className={styles.infoCard}>
            <div className={styles.infoIcon}>✨</div>
            <h2 className={styles.infoTitle}>Personalized Learning</h2>
            <p className={styles.infoText}>
              Receive explanations tailored to your background and learning style. Practice with
              custom examples and exercises.
            </p>
          </div>
        </div>

        <div className={styles.ctaSection}>
          <button
            className={styles.openChatButton}
            onClick={() => setIsChatOpen(true)}
          >
            Open Study Assistant
          </button>
          <p className={styles.ctaNote}>
            Note: Backend integration coming soon. Currently showing UI placeholder.
          </p>
        </div>
      </div>

      <ChatPanelPlaceholder
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </Layout>
  );
}
