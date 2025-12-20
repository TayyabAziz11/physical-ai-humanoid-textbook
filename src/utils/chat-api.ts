/**
 * Chat API client for interacting with the RAG backend.
 * Properly integrated with Docusaurus configuration.
 */

export interface QueryResponse {
  answer: string;
  citations?: Citation[];
  mode: 'global' | 'selection';
}

export interface Citation {
  section_title: string;
  source_file: string;
  link_url: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Get the API base URL.
 * For development: uses localhost:8000
 * For production: set window.CHAT_API_URL in your deployment
 */
function getApiBaseUrl(): string {
  // Check if we're in a browser context
  if (typeof window !== 'undefined') {
    // Allow runtime configuration via window object (set in production)
    const configuredUrl = (window as any).CHAT_API_URL;
    if (configuredUrl) {
      return configuredUrl;
    }
  }

  // Default to localhost for development
  return 'http://localhost:8000/api/v1';
}

/**
 * Query the entire textbook using RAG (Retrieval-Augmented Generation).
 *
 * @param question - User's question
 * @param conversationHistory - Optional conversation history for context
 * @returns Query response with answer and citations
 */
export async function queryGlobal(
  question: string,
  conversationHistory: ConversationMessage[] | null = null
): Promise<QueryResponse> {
  const apiBaseUrl = getApiBaseUrl();

  const requestBody: Record<string, unknown> = {
    question: question.trim(),
  };

  if (conversationHistory && conversationHistory.length > 0) {
    requestBody.conversation_history = conversationHistory;
  }

  const response = await fetch(`${apiBaseUrl}/query/global`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    let errorMessage = `API request failed with status ${response.status}`;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If parsing JSON fails, use the default error message
    }

    throw new Error(errorMessage);
  }

  const data = await response.json();
  return data as QueryResponse;
}

/**
 * Query specific selected text using direct GPT-4 processing.
 *
 * @param question - User's question about the selected text
 * @param selectedText - The text selected by the user
 * @returns Query response with answer (no citations in selection mode)
 */
export async function querySelection(
  question: string,
  selectedText: string
): Promise<QueryResponse> {
  const apiBaseUrl = getApiBaseUrl();

  const requestBody = {
    question: question.trim(),
    selected_text: selectedText.trim(),
  };

  const response = await fetch(`${apiBaseUrl}/query/selection`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    let errorMessage = `API request failed with status ${response.status}`;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If parsing JSON fails, use the default error message
    }

    throw new Error(errorMessage);
  }

  const data = await response.json();
  return data as QueryResponse;
}
