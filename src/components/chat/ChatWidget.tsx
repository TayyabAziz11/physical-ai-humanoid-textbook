import React, { useState, useEffect, useRef } from 'react';
import styles from './ChatPanelPlaceholder.module.css'; // Reuse existing styles
import { queryGlobal, querySelection } from '@site/src/utils/chat-api';

export interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
  selectedText?: string;
  initialMode?: 'whole-book' | 'selection';
}

type ChatMode = 'whole-book' | 'selection';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
  isError?: boolean;
}

interface Citation {
  section_title: string;
  source_file: string;
  link_url: string;
}

export default function ChatWidget({
  isOpen,
  onClose,
  className,
  selectedText = '',
  initialMode = 'whole-book'
}: ChatWidgetProps): JSX.Element {
  const [mode, setMode] = useState<ChatMode>(initialMode);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [capturedSelection, setCapturedSelection] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update mode and capture selection when panel opens
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      if (initialMode === 'selection' && selectedText) {
        setCapturedSelection(selectedText);
      }
    }
  }, [isOpen, initialMode, selectedText]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputText.trim() || isLoading) {
      return;
    }

    const userQuestion = inputText.trim();

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userQuestion,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      let response;

      if (mode === 'whole-book') {
        // Global query mode
        response = await queryGlobal(userQuestion);
      } else {
        // Selection query mode
        const textToQuery = capturedSelection || selectedText;

        if (!textToQuery) {
          throw new Error('No text selected. Please select text first or switch to whole-book mode.');
        }

        response = await querySelection(userQuestion, textToQuery);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        citations: response.citations || [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: error instanceof Error
          ? error.message
          : 'An unexpected error occurred. Please try again.',
        timestamp: new Date(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = (newMode: ChatMode) => {
    setMode(newMode);

    // Clear captured selection when switching to whole-book mode
    if (newMode === 'whole-book') {
      setCapturedSelection('');
    } else if (newMode === 'selection' && selectedText) {
      setCapturedSelection(selectedText);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className={`${styles.overlay} ${className || ''}`} onClick={onClose}>
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title}>Study Assistant</h2>
          <div style={{ display: 'flex', gap: '8px' }}>
            {messages.length > 0 && (
              <button
                className={styles.closeButton}
                onClick={handleClearChat}
                aria-label="Clear chat history"
                title="Clear chat"
                style={{ fontSize: '14px' }}
              >
                🗑️
              </button>
            )}
            <button
              className={styles.closeButton}
              onClick={onClose}
              aria-label="Close chat panel"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Mode selector */}
        <div className={styles.modeSelector}>
          <button
            className={`${styles.modeButton} ${mode === 'whole-book' ? styles.active : ''}`}
            onClick={() => handleModeChange('whole-book')}
            aria-pressed={mode === 'whole-book'}
          >
            📚 Whole-book Q&A
          </button>
          <button
            className={`${styles.modeButton} ${mode === 'selection' ? styles.active : ''}`}
            onClick={() => handleModeChange('selection')}
            aria-pressed={mode === 'selection'}
            disabled={!capturedSelection && !selectedText}
          >
            🔍 Selection-based Q&A
          </button>
        </div>

        {/* Messages area */}
        <div className={styles.content}>
          {/* Show selected text context if in selection mode */}
          {mode === 'selection' && (capturedSelection || selectedText) && (
            <div className={styles.selectedTextContext}>
              <div className={styles.contextLabel}>📝 Selected Text:</div>
              <div className={styles.contextText}>
                "{capturedSelection || selectedText}"
              </div>
            </div>
          )}

          {/* Messages list */}
          {messages.length === 0 ? (
            <div className={styles.placeholderMessage}>
              <div className={styles.iconLarge}>💬</div>
              <h3 className={styles.placeholderTitle}>Ask a Question</h3>
              <p className={styles.placeholderText}>
                {mode === 'whole-book'
                  ? 'Ask questions about any topic in the entire textbook. I\'ll search through all chapters to find relevant information.'
                  : capturedSelection || selectedText
                    ? 'Ask questions about the selected text above. I\'ll answer based only on the highlighted content.'
                    : 'Please select text on the page to ask questions about it.'
                }
              </p>
            </div>
          ) : (
            <div className={styles.messagesList}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`${styles.messageWrapper} ${styles[message.role]}`}
                >
                  <div
                    className={`${styles.messageBubble} ${styles[message.role]} ${
                      message.isError ? styles.error : ''
                    }`}
                  >
                    <div className={styles.messageContent}>
                      {message.content}
                    </div>

                    {/* Citations */}
                    {message.citations && message.citations.length > 0 && (
                      <div className={styles.citations}>
                        <div className={styles.citationsHeader}>
                          📖 Sources:
                        </div>
                        {message.citations.map((citation, idx) => (
                          <div key={idx} className={styles.citation}>
                            <a
                              href={citation.link_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              {citation.section_title}
                            </a>
                            {' '}
                            <span className={styles.citationSource}>
                              ({citation.source_file})
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className={styles.messageTimestamp}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className={styles.loadingIndicator}>
                  <div className={styles.loadingDots}>
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                  <span>Thinking...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <form onSubmit={handleSubmit} className={styles.inputArea}>
          <input
            ref={inputRef}
            type="text"
            className={styles.input}
            placeholder={
              mode === 'selection' && !capturedSelection && !selectedText
                ? 'Select text first...'
                : 'Ask a question...'
            }
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isLoading || (mode === 'selection' && !capturedSelection && !selectedText)}
            aria-label="Chat input"
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={isLoading || !inputText.trim() || (mode === 'selection' && !capturedSelection && !selectedText)}
            aria-label="Send message"
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
}
