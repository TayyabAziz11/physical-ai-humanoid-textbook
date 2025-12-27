import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Bridging the gap between digital intelligence and the physical world through embodied AI',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // GitHub Pages deployment config
  url: 'https://TayyabAziz11.github.io',
  baseUrl: '/physical-ai-humanoid-textbook/',
  organizationName: 'TayyabAziz11',
  projectName: 'physical-ai-humanoid-textbook',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Internationalization with local translation files (Docusaurus official i18n)
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'], // Only English and Urdu have full translations
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
        htmlLang: 'ur',
      },
      // Future locales (uncomment when translations are ready):
      // ja: {
      //   label: '日本語',
      //   direction: 'ltr',
      //   htmlLang: 'ja',
      // },
      // es: {
      //   label: 'Español',
      //   direction: 'ltr',
      //   htmlLang: 'es-ES',
      // },
      // ar: {
      //   label: 'العربية',
      //   direction: 'rtl',
      //   htmlLang: 'ar',
      // },
      // fr: {
      //   label: 'Français',
      //   direction: 'ltr',
      //   htmlLang: 'fr-FR',
      // },
      // 'zh-Hans': {
      //   label: '中文',
      //   direction: 'ltr',
      //   htmlLang: 'zh-CN',
      // },
    },
  },

  // Custom head tags for cache-busting and version metadata
  headTags: [
    {
      tagName: 'meta',
      attributes: {
        name: 'app-version',
        content: '1.0.1',
      },
    },
    {
      tagName: 'meta',
      attributes: {
        name: 'build-date',
        content: new Date().toISOString(),
      },
    },
    {
      tagName: 'meta',
      attributes: {
        'http-equiv': 'Cache-Control',
        content: 'no-cache, no-store, must-revalidate',
      },
    },
    {
      tagName: 'meta',
      attributes: {
        'http-equiv': 'Pragma',
        content: 'no-cache',
      },
    },
    {
      tagName: 'meta',
      attributes: {
        'http-equiv': 'Expires',
        content: '0',
      },
    },
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: false,  // Hide blog entirely
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    // Custom configuration for ChatWidget
    customFields: {
      // Backend API URL is now managed in src/config/api-config.ts
      // Railway production: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app
      apiVersion: '1.0.1',
      buildTimestamp: new Date().toISOString(),
    },
    metadata: [
      // Additional cache-busting meta tags
      {name: 'version', content: '1.0.1'},
      {name: 'last-updated', content: new Date().toISOString()},
    ],
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course',
        },
        {
          to: '/chat',
          label: 'Study Assistant',
          position: 'left',
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/TayyabAziz11',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Course Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Study Assistant',
              to: '/chat',
            },
          ],
        },
        {
          title: 'Connect',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/TayyabAziz11',
            },
            {
              label: 'LinkedIn',
              href: 'https://www.linkedin.com/in/tayyab-aziz-763a502b4/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Authored by Tayyab Aziz. v1.0.1`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
