import React, { useState, useEffect, useCallback } from 'react';
import AskTheTextbookButton from '@site/src/components/chat/AskTheTextbookButton';
import ChatWidget from '@site/src/components/chat/ChatWidget';
import TextSelectionTooltip from '@site/src/components/chat/TextSelectionTooltip';

const MIN_SELECTION_LENGTH = 10;

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedText, setSelectedText] = useState<string>('');
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [initialMode, setInitialMode] = useState<'whole-book' | 'selection'>('whole-book');

  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();

    if (!selection || selection.rangeCount === 0) {
      setTooltipVisible(false);
      return;
    }

    const text = selection.toString().trim();

    // Only show tooltip if selection is at least MIN_SELECTION_LENGTH characters
    if (text.length >= MIN_SELECTION_LENGTH) {
      try {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Position tooltip near the end of the selection
        const x = rect.right + window.scrollX;
        const y = rect.bottom + window.scrollY + 5; // 5px below selection

        setSelectedText(text);
        setTooltipPosition({ x, y });
        setTooltipVisible(true);
      } catch (error) {
        // If getBoundingClientRect fails, hide tooltip
        setTooltipVisible(false);
      }
    } else {
      setTooltipVisible(false);
    }
  }, []);

  const handleAskAboutSelection = useCallback(() => {
    // Open chat panel in selection mode with the selected text
    setInitialMode('selection');
    setIsChatOpen(true);
    setTooltipVisible(false);
  }, []);

  const handleChatClose = useCallback(() => {
    setIsChatOpen(false);
    // Reset to whole-book mode when closing
    setInitialMode('whole-book');
  }, []);

  useEffect(() => {
    // Add event listeners for text selection
    const handleMouseUp = () => {
      // Small delay to ensure selection is complete
      setTimeout(handleTextSelection, 10);
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Handle keyboard selection (arrow keys with shift, etc.)
      if (e.shiftKey || e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        setTimeout(handleTextSelection, 10);
      }
    };

    const handleSelectionChange = () => {
      // Hide tooltip when selection is cleared
      const selection = window.getSelection();
      if (selection && selection.toString().trim().length < MIN_SELECTION_LENGTH) {
        setTooltipVisible(false);
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keyup', handleKeyUp);
    document.addEventListener('selectionchange', handleSelectionChange);

    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('keyup', handleKeyUp);
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, [handleTextSelection]);

  return (
    <>
      {children}

      {/* Floating chat button - visible on all pages except /chat */}
      {typeof window !== 'undefined' && !window.location.pathname.includes('/chat') && (
        <AskTheTextbookButton onClick={() => setIsChatOpen(true)} />
      )}

      {/* Text selection tooltip */}
      <TextSelectionTooltip
        isVisible={tooltipVisible}
        position={tooltipPosition}
        onAskAboutSelection={handleAskAboutSelection}
      />

      {/* Chat panel */}
      <ChatWidget
        isOpen={isChatOpen}
        onClose={handleChatClose}
        selectedText={selectedText}
        initialMode={initialMode}
      />
    </>
  );
}
