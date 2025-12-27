# Multilingual Translation Guide

Welcome to the multilingual translation feature! This guide will help you translate any content in this textbook to your preferred language.

## Overview

The translation feature allows you to:
- Translate selected text from any page to 7 supported languages
- Translate chatbot responses to your preferred language
- View translations with proper right-to-left (RTL) support for Arabic and Urdu
- Automatically cache translations for faster repeated access

All translations are powered by OpenAI GPT-4o-mini and preserve technical terminology in English for accuracy.

## Supported Languages

| Language | Native Name | Script Direction |
|----------|-------------|------------------|
| 🇬🇧 English | English | Left-to-Right |
| 🇵🇰 Urdu | اردو | **Right-to-Left** |
| 🇸🇦 Arabic | العربية | **Right-to-Left** |
| 🇪🇸 Spanish | Español | Left-to-Right |
| 🇨🇳 Mandarin Chinese | 中文 | Left-to-Right |
| 🇯🇵 Japanese | 日本語 | Left-to-Right |
| 🇫🇷 French | Français | Left-to-Right |

:::tip Right-to-Left Languages
Arabic and Urdu are displayed with proper right-to-left text direction for natural reading.
:::

## How to Translate Selected Text

### Step 1: Select Text

Use your mouse or keyboard to select any text on the page. The text can be:
- A single word
- A sentence or paragraph
- Up to 1,500 characters

:::info Selection Limits
Selections longer than 1,500 characters will be rejected. For longer content, translate in smaller sections.
:::

### Step 2: Choose Your Language

When you select text, a translation panel will appear near your selection with:
- A **language selector dropdown** showing all 7 supported languages
- A **Translate button**

Click the language dropdown and select your preferred target language.

### Step 3: Translate

Click the **Translate** button. You'll see a loading indicator while the translation is being processed.

### Step 4: View Translation

A modal window will appear showing:
- **Original Text**: The text you selected (can be hidden if desired)
- **Translated Text**: The translation in your chosen language
- **Language Information**: Source and target languages with flags
- **Cache Status**: Whether the translation was loaded from cache (⚡ Cached badge)

### Step 5: Copy or Close

You can:
- **Copy** the translated text to your clipboard using the 📋 Copy button
- **Toggle** the original text visibility with the Show/Hide button
- **Close** the modal by clicking the X button, clicking outside, or pressing Escape

## Translation Features

### Technical Terms Preservation

By default, technical terms remain in English to ensure accuracy. For example:
- "ROS 2" stays as "ROS 2" in all languages
- "SLAM" stays as "SLAM"
- "Docker" stays as "Docker"

This ensures that technical documentation remains clear and searchable.

### Client-Side Caching

Translations are automatically cached in your browser for 7 days. This means:
- ✅ **Faster**: Repeated translations load instantly
- ✅ **Privacy**: Translations are stored only on your device
- ✅ **Offline Access**: Cached translations work without internet
- ✅ **No Server Load**: Reduces API calls and costs

The cache automatically manages itself:
- Old translations expire after 7 days
- Maximum 50 translations per language
- Least recently used translations are removed when the cache is full

### Right-to-Left (RTL) Support

Arabic and Urdu translations automatically display with proper right-to-left text direction:
- Text flows from right to left
- Punctuation appears correctly
- Mixed content (English terms in Arabic/Urdu) renders properly

## Common Scenarios

### Translating a Code Example

When translating content that includes code examples:
1. Select only the text description, not the code itself
2. Code blocks and technical terms remain in their original form
3. Comments can be translated if selected separately

### Translating Multiple Sections

To translate multiple paragraphs:
1. Translate one section at a time (max 1,500 characters)
2. Each translation can be copied and saved separately
3. All translations are cached for quick access later

### Switching Languages

To view the same text in multiple languages:
1. Select the text again after closing the modal
2. Choose a different target language
3. Translate again (cached translations load instantly)

## Troubleshooting

### "Rate limit exceeded" Error

**Problem**: You've made too many translation requests in a short time.

**Solution**: Wait 1 minute before translating again. The limit is 10 translations per minute per user.

### "Selection too long" Error

**Problem**: The selected text exceeds 1,500 characters.

**Solution**: Select a smaller portion of text and translate it in sections.

### "Translation failed" Error

**Possible Causes**:
- Temporary network issue
- Backend service unavailable
- Invalid text selection

**Solutions**:
1. Check your internet connection
2. Try selecting the text again
3. Refresh the page and retry
4. If the problem persists, wait a few minutes

### Translation Not Appearing

**Possible Causes**:
- Text selection was too short or contained only whitespace
- JavaScript is disabled in your browser
- Ad blocker or privacy extension blocking the feature

**Solutions**:
1. Ensure you've selected actual text (not just spaces)
2. Enable JavaScript
3. Temporarily disable extensions and retry

## Privacy & Data

### What We Store

- **On your device**: Translated text cached in localStorage (up to 7 days)
- **On our servers**: No user data or translations are permanently stored

### What We Don't Store

- ❌ Original book content
- ❌ User selections
- ❌ Translation history beyond local cache
- ❌ Personal information

### Data Transmission

When you translate text:
1. Selected text is sent to our backend API
2. The backend calls OpenAI's API for translation
3. The translation is returned to your browser
4. Both request and response are temporary and not logged

:::info Privacy-First Design
We never store your selections or translations on our servers. All caching happens in your browser.
:::

## Tips for Best Results

### 1. Select Complete Sentences

For better translation quality, select complete sentences or paragraphs rather than isolated words.

### 2. Provide Context

The translation system works best with natural language. Complete thoughts translate more accurately than fragments.

### 3. Technical Content

For highly technical content, keep the English version visible to cross-reference technical terms.

### 4. Long Documents

For translating entire chapters:
- Use the chatbot to ask questions in your language
- Translate key sections as needed
- Keep a reference document with important translations

## Frequently Asked Questions

### Can I translate the entire textbook?

Currently, you can translate selected portions up to 1,500 characters at a time. For full-chapter translations, use the chatbot and ask questions in your preferred language.

### Are translations machine-generated or human-reviewed?

All translations are generated by OpenAI GPT-4o-mini. While generally accurate, machine translations may occasionally miss nuances. Always refer to the English version for critical technical details.

### Can I suggest a new language?

Language support is currently limited to the 7 languages listed above. Feature requests can be submitted via GitHub issues.

### Will my language preference be remembered?

Yes! Your last-selected target language is saved in your browser and will be pre-selected the next time you translate.

### Does translation work offline?

Cached translations work offline. New translations require an internet connection to contact the translation API.

### How accurate are the translations?

Translations are powered by OpenAI's GPT-4o-mini model, which provides high-quality results for general and technical content. Technical terms are preserved in English to maintain accuracy.

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Close translation modal | `Escape` key |
| Select text | Mouse drag or `Shift + Arrow keys` |
| Copy translation | Use 📋 Copy button (no keyboard shortcut) |

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the FAQ** above
2. **Refresh the page** and try again
3. **Clear your browser cache** if translations seem incorrect
4. **Report an issue** on our GitHub repository

---

**Happy translating!** 🌐

We hope this feature makes the textbook more accessible to learners around the world.
