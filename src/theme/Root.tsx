import React, { useState } from 'react';
import AskTheTextbookButton from '@site/src/components/chat/AskTheTextbookButton';
import ChatPanelPlaceholder from '@site/src/components/chat/ChatPanelPlaceholder';

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <>
      {children}

      {/* Floating chat button - visible on all pages except /chat */}
      {typeof window !== 'undefined' && !window.location.pathname.includes('/chat') && (
        <AskTheTextbookButton onClick={() => setIsChatOpen(true)} />
      )}

      {/* Chat panel */}
      <ChatPanelPlaceholder
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
}
