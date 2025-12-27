/**
 * ContentTranslator - Automatically translates page content based on selected language
 * Uses aggressive caching and chunk-based translation for better performance
 */

import React, { useEffect, useState, ReactNode } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from '../../hooks/useTranslation';
import styles from './ContentTranslator.module.css';

export interface ContentTranslatorProps {
  children: ReactNode;
  /** Whether this content should be translated */
  translatable?: boolean;
}

export default function ContentTranslator({
  children,
  translatable = true,
}: ContentTranslatorProps): JSX.Element {
  const { currentLanguage, isRTL } = useLanguage();
  const { translate, isTranslating } = useTranslation();
  const [translatedContent, setTranslatedContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset translation when switching back to English
    if (currentLanguage === 'english') {
      setTranslatedContent(null);
      setError(null);
      return;
    }

    // Don't translate if not translatable
    if (!translatable) {
      return;
    }

    // Extract text content from children
    const textContent = extractTextContent(children);
    if (!textContent || textContent.length === 0) {
      return;
    }

    // Translate content in chunks if needed (max 1500 chars per request)
    const translateContent = async () => {
      try {
        const chunks = chunkText(textContent, 1500);
        const translatedChunks: string[] = [];

        for (const chunk of chunks) {
          const result = await translate(chunk, currentLanguage, {
            preserveTechnicalTerms: true,
          });

          if (result) {
            translatedChunks.push(result.translated_text);
          } else {
            // Fallback to original text if translation fails
            translatedChunks.push(chunk);
          }
        }

        setTranslatedContent(translatedChunks.join('\n\n'));
        setError(null);
      } catch (err) {
        console.error('Content translation error:', err);
        setError(err instanceof Error ? err.message : 'Translation failed');
        setTranslatedContent(null);
      }
    };

    translateContent();
  }, [children, currentLanguage, translatable, translate]);

  // Show loading state
  if (isTranslating && !translatedContent) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner} />
        <span className={styles.loadingText}>Translating page...</span>
      </div>
    );
  }

  // Show error state (with original content)
  if (error) {
    return (
      <div>
        <div className={styles.errorBanner}>
          ⚠️ Translation unavailable. Showing original content.
        </div>
        {children}
      </div>
    );
  }

  // Show translated content
  if (translatedContent && currentLanguage !== 'english') {
    return (
      <div dir={isRTL ? 'rtl' : 'ltr'} className={styles.translatedContent}>
        <div className={styles.translationBadge}>
          🌐 Translated to {currentLanguage}
        </div>
        <div dangerouslySetInnerHTML={{ __html: formatTranslatedText(translatedContent) }} />
      </div>
    );
  }

  // Show original content
  return <>{children}</>;
}

// Helper functions

function extractTextContent(children: ReactNode): string {
  if (typeof children === 'string') {
    return children;
  }

  if (Array.isArray(children)) {
    return children.map(extractTextContent).filter(Boolean).join(' ');
  }

  if (React.isValidElement(children)) {
    // @ts-expect-error - children.props.children might not exist
    return extractTextContent(children.props?.children);
  }

  return '';
}

function chunkText(text: string, maxLength: number): string[] {
  if (text.length <= maxLength) {
    return [text];
  }

  const chunks: string[] = [];
  let currentChunk = '';

  // Split by paragraphs first
  const paragraphs = text.split(/\n\n+/);

  for (const paragraph of paragraphs) {
    if (currentChunk.length + paragraph.length + 2 <= maxLength) {
      currentChunk += (currentChunk ? '\n\n' : '') + paragraph;
    } else {
      if (currentChunk) {
        chunks.push(currentChunk);
      }
      currentChunk = paragraph;

      // If a single paragraph is too long, split by sentences
      if (currentChunk.length > maxLength) {
        const sentences = currentChunk.match(/[^.!?]+[.!?]+/g) || [currentChunk];
        currentChunk = '';

        for (const sentence of sentences) {
          if (currentChunk.length + sentence.length <= maxLength) {
            currentChunk += sentence;
          } else {
            if (currentChunk) {
              chunks.push(currentChunk);
            }
            currentChunk = sentence;
          }
        }
      }
    }
  }

  if (currentChunk) {
    chunks.push(currentChunk);
  }

  return chunks;
}

function formatTranslatedText(text: string): string {
  // Preserve line breaks and basic formatting
  return text
    .split('\n')
    .map(line => `<p>${line}</p>`)
    .join('');
}
