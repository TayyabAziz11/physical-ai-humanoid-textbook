---
sidebar_position: 2
---

# اپنی سائٹ کا ترجمہ کریں

آئیے `docs/intro.md` کو French میں ترجمہ کرتے ہیں۔

## i18n کو Configure کریں

`fr` locale کے لیے سپورٹ شامل کرنے کے لیے `docusaurus.config.js` میں ترمیم کریں:

```js title="docusaurus.config.js"
export default {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr'],
  },
};
```

## ایک doc کا ترجمہ کریں

`docs/intro.md` فائل کو `i18n/fr` فولڈر میں کاپی کریں:

```bash
mkdir -p i18n/fr/docusaurus-plugin-content-docs/current/

cp docs/intro.md i18n/fr/docusaurus-plugin-content-docs/current/intro.md
```

`i18n/fr/docusaurus-plugin-content-docs/current/intro.md` کو French میں ترجمہ کریں۔

## اپنی localized سائٹ شروع کریں

French locale پر اپنی سائٹ شروع کریں:

```bash
npm run start -- --locale fr
```

آپ کی localized سائٹ [http://localhost:3000/fr/](http://localhost:3000/fr/) پر قابل رسائی ہے اور `Getting Started` صفحہ کا ترجمہ ہو چکا ہے۔

:::caution احتیاط

Development میں، آپ ایک وقت میں صرف ایک locale استعمال کر سکتے ہیں۔

:::

## ایک Locale Dropdown شامل کریں

زبانوں میں آسانی سے navigate کرنے کے لیے، ایک locale dropdown شامل کریں۔

`docusaurus.config.js` فائل میں ترمیم کریں:

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'localeDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

Locale dropdown اب آپ کے navbar میں ظاہر ہوتا ہے:

![Locale Dropdown](./img/localeDropdown.png)

## اپنی localized سائٹ build کریں

کسی مخصوص locale کے لیے اپنی سائٹ build کریں:

```bash
npm run build -- --locale fr
```

یا اپنی سائٹ کو ایک ساتھ تمام locales شامل کرتے ہوئے build کریں:

```bash
npm run build
```
