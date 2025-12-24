/**
 * API Configuration for Railway Backend
 *
 * This file manages the backend URL configuration for both development and production.
 * Version: 1.0.1 (Updated 2025-12-23)
 */

export const API_CONFIG = {
  // Production Railway backend URL
  PRODUCTION_URL: 'https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app',

  // Development localhost URL
  DEVELOPMENT_URL: 'http://localhost:8000',

  // API version
  VERSION: '1.0.1',

  // Last updated timestamp (for cache busting)
  LAST_UPDATED: '2025-12-23T12:00:00Z',
} as const;

/**
 * Get the correct API base URL based on environment.
 *
 * Priority:
 * 1. window.CHAT_API_URL (runtime override for testing)
 * 2. Production URL (if hostname is GitHub Pages)
 * 3. Development URL (for local development)
 */
export function getApiBaseUrl(): string {
  // Browser environment check
  if (typeof window === 'undefined') {
    return API_CONFIG.PRODUCTION_URL;
  }

  // Runtime override (highest priority)
  const runtimeUrl = (window as any).CHAT_API_URL;
  if (runtimeUrl) {
    console.log('🔧 Using runtime API URL:', runtimeUrl);
    return runtimeUrl;
  }

  // Check if we're on GitHub Pages (production)
  const isGitHubPages =
    window.location.hostname.includes('github.io') ||
    window.location.hostname.includes('TayyabAziz11.github.io');

  // Check if we're on localhost (development)
  const isLocalhost =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '';

  if (isGitHubPages) {
    console.log('🚀 Production mode - Using Railway backend:', API_CONFIG.PRODUCTION_URL);
    return API_CONFIG.PRODUCTION_URL;
  }

  if (isLocalhost) {
    console.log('🔧 Development mode - Using localhost:', API_CONFIG.DEVELOPMENT_URL);
    return API_CONFIG.DEVELOPMENT_URL;
  }

  // Default to production for any other deployment
  console.log('🌐 Unknown environment - Defaulting to production:', API_CONFIG.PRODUCTION_URL);
  return API_CONFIG.PRODUCTION_URL;
}

/**
 * Get full API endpoint URL
 */
export function getApiEndpoint(path: string): string {
  const baseUrl = getApiBaseUrl();
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
}

/**
 * Verify API connectivity
 */
export async function verifyApiConnection(): Promise<boolean> {
  try {
    const baseUrl = getApiBaseUrl();
    const response = await fetch(`${baseUrl}/health`, {
      method: 'GET',
      cache: 'no-cache', // Always bypass cache for health checks
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ API Connection verified:', data);
      return true;
    }

    console.error('❌ API Health check failed:', response.status);
    return false;
  } catch (error) {
    console.error('❌ API Connection error:', error);
    return false;
  }
}

// Log configuration on import (helps with debugging)
if (typeof window !== 'undefined') {
  console.log('📡 API Config loaded:', {
    version: API_CONFIG.VERSION,
    lastUpdated: API_CONFIG.LAST_UPDATED,
    currentUrl: getApiBaseUrl(),
  });
}
