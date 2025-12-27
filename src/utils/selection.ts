/**
 * Utilities for handling text selection in the browser.
 *
 * @module selection
 */

/**
 * Maximum allowed selection length for translation (characters).
 */
export const MAX_SELECTION_LENGTH = 1500;

/**
 * Get the currently selected text from the window.
 *
 * @returns Selected text or null if no selection
 */
export function getSelectedText(): string | null {
  if (typeof window === 'undefined') return null;

  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return null;

  const text = selection.toString().trim();
  return text.length > 0 ? text : null;
}

/**
 * Check if a selection is valid for translation.
 *
 * @param text - Selected text to validate
 * @returns Validation result with error message if invalid
 */
export function validateSelection(text: string | null): {
  valid: boolean;
  error?: string;
} {
  if (!text) {
    return { valid: false, error: 'No text selected' };
  }

  if (text.length > MAX_SELECTION_LENGTH) {
    return {
      valid: false,
      error: `Selection too long. Maximum ${MAX_SELECTION_LENGTH} characters allowed.`,
    };
  }

  // Check if text is just whitespace
  if (text.trim().length === 0) {
    return { valid: false, error: 'Selection contains only whitespace' };
  }

  return { valid: true };
}

/**
 * Get the bounding rectangle of the current selection.
 *
 * @returns DOMRect of the selection or null
 */
export function getSelectionRect(): DOMRect | null {
  if (typeof window === 'undefined') return null;

  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return null;

  const range = selection.getRangeAt(0);
  return range.getBoundingClientRect();
}

/**
 * Clear the current text selection.
 */
export function clearSelection(): void {
  if (typeof window === 'undefined') return;

  const selection = window.getSelection();
  if (selection) {
    selection.removeAllRanges();
  }
}

/**
 * Check if the selection is within a specific container element.
 *
 * @param containerSelector - CSS selector for container
 * @returns True if selection is within container
 */
export function isSelectionInContainer(containerSelector: string): boolean {
  if (typeof window === 'undefined') return false;

  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return false;

  const range = selection.getRangeAt(0);
  const container = range.commonAncestorContainer;

  // Check if container or any parent matches the selector
  let element: Element | null =
    container.nodeType === Node.ELEMENT_NODE
      ? (container as Element)
      : container.parentElement;

  while (element) {
    if (element.matches(containerSelector)) {
      return true;
    }
    element = element.parentElement;
  }

  return false;
}
