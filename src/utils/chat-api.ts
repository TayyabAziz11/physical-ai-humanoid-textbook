/**
 * Chat API client for interacting with the RAG backend.
 * Updated to use centralized API configuration with proper cache-busting.
 * Version: 1.0.1 (Updated 2025-12-23)
 */

import { getApiEndpoint } from '../config/api-config';

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
 * Fetch with cache-busting headers.
 * Ensures we always get fresh data from the backend.
 */
async function fetchWithCacheBusting(url: string, options: RequestInit = {}): Promise<Response> {
  const timestamp = Date.now();
  const cacheBustedUrl = url.includes('?')
    ? `${url}&_t=${timestamp}`
    : `${url}?_t=${timestamp}`;

  const headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    ...options.headers,
  };

  return fetch(cacheBustedUrl, {
    ...options,
    headers,
  });
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
  const endpoint = getApiEndpoint('/api/v1/query/global');

  console.log('📤 Sending global query to:', endpoint);

  const requestBody: Record<string, unknown> = {
    question: question.trim(),
  };

  if (conversationHistory && conversationHistory.length > 0) {
    requestBody.conversation_history = conversationHistory;
  }

  const response = await fetchWithCacheBusting(endpoint, {
    method: 'POST',
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

    console.error('❌ Global query failed:', errorMessage);
    throw new Error(errorMessage);
  }

  const data = await response.json();
  console.log('✅ Global query successful');
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
  const endpoint = getApiEndpoint('/api/v1/query/selection');

  console.log('📤 Sending selection query to:', endpoint);

  const requestBody = {
    question: question.trim(),
    selected_text: selectedText.trim(),
  };

  const response = await fetchWithCacheBusting(endpoint, {
    method: 'POST',
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

    console.error('❌ Selection query failed:', errorMessage);
    throw new Error(errorMessage);
  }

  const data = await response.json();
  console.log('✅ Selection query successful');
  return data as QueryResponse;
}
