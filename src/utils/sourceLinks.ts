/**
 * Source Link Utilities - Fix chatbot citation links to work with Docusaurus routing
 */

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

export interface SourceLinkMetadata {
  sourceFile: string;
  sectionTitle: string;
  linkUrl: string;
}

/**
 * Fix a source link URL to work with Docusaurus routing.
 * Backend returns URLs like "/intro#getting-started" but Docusaurus needs
 * "/physical-ai-humanoid-textbook/intro#getting-started" (with baseUrl).
 *
 * @param backendUrl - The URL returned by the backend (e.g., "/intro#getting-started")
 * @param baseUrl - Docusaurus baseUrl (e.g., "/physical-ai-humanoid-textbook/")
 * @returns Fixed URL that works in Docusaurus
 */
export function fixSourceLink(backendUrl: string, baseUrl: string = '/'): string {
  // Remove leading slash if present
  const cleanUrl = backendUrl.startsWith('/') ? backendUrl.slice(1) : backendUrl;

  // Remove trailing slash from baseUrl if present
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  // Combine baseUrl with the clean URL
  return `${cleanBaseUrl}/${cleanUrl}`;
}

/**
 * Build a Docusaurus-compatible link from source file and section title.
 * This mirrors the backend logic but adds the correct baseUrl.
 *
 * @param sourceFile - Source file path (e.g., "docs/intro.md")
 * @param sectionTitle - Section heading (e.g., "Getting Started")
 * @param baseUrl - Docusaurus baseUrl
 * @returns Docusaurus-compatible URL
 */
export function buildDocusaurusLink(
  sourceFile: string,
  sectionTitle: string,
  baseUrl: string = '/'
): string {
  // Convert file path to URL path (remove docs/ prefix and .md extension)
  let urlPath = sourceFile.replace(/^docs\//, '').replace(/\.mdx?$/, '');

  // Handle special cases
  if (urlPath === 'index' || urlPath === 'README') {
    urlPath = '';
  }

  // Convert section title to URL fragment (lowercase, replace spaces with hyphens)
  let sectionFragment = sectionTitle
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Remove duplicate hyphens
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens

  // Remove trailing slash from baseUrl if present
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  // Build final URL
  if (sectionFragment) {
    return `${cleanBaseUrl}/${urlPath}#${sectionFragment}`;
  } else {
    return `${cleanBaseUrl}/${urlPath}`;
  }
}

/**
 * React hook to get the base URL from Docusaurus context.
 * Use this to get the correct baseUrl for fixing source links.
 *
 * @returns baseUrl from Docusaurus config
 */
export function useBaseUrl(): string {
  const { siteConfig } = useDocusaurusContext();
  return siteConfig.baseUrl;
}

/**
 * Validate that a source link will work in the current Docusaurus site.
 * This checks if the URL includes the correct baseUrl.
 *
 * @param url - URL to validate
 * @param baseUrl - Expected baseUrl
 * @returns true if URL is valid for this site
 */
export function isValidSourceLink(url: string, baseUrl: string = '/'): boolean {
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  // URL should start with baseUrl (or be relative without baseUrl for development)
  return url.startsWith(cleanBaseUrl) || url.startsWith('/');
}

/**
 * Extract metadata from a source file path.
 * Useful for debugging and logging.
 *
 * @param sourceFile - Source file path (e.g., "docs/chapter1/intro.md")
 * @returns Metadata object with file info
 */
export function extractSourceFileMetadata(sourceFile: string): {
  directory: string;
  fileName: string;
  extension: string;
  isMarkdown: boolean;
} {
  const parts = sourceFile.split('/');
  const fileName = parts[parts.length - 1];
  const fileNameParts = fileName.split('.');
  const extension = fileNameParts.length > 1 ? fileNameParts[fileNameParts.length - 1] : '';

  return {
    directory: parts.slice(0, -1).join('/'),
    fileName: fileNameParts[0],
    extension,
    isMarkdown: extension === 'md' || extension === 'mdx',
  };
}
