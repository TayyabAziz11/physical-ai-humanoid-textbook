---
sidebar_position: 1
---

# Docs Versions کا انتظام کریں

Docusaurus آپ کے docs کے متعدد versions کا انتظام کر سکتا ہے۔

## ایک docs version بنائیں

اپنے پروجیکٹ کا version 1.0 release کریں:

```bash
npm run docusaurus docs:version 1.0
```

`docs` فولڈر کو `versioned_docs/version-1.0` میں کاپی کیا جاتا ہے اور `versions.json` بنایا جاتا ہے۔

اب آپ کے docs کے 2 versions ہیں:

- `1.0` پر `http://localhost:3000/docs/` version 1.0 docs کے لیے
- `current` پر `http://localhost:3000/docs/next/` **آنے والے، unreleased docs** کے لیے

## ایک Version Dropdown شامل کریں

Versions میں آسانی سے navigate کرنے کے لیے، ایک version dropdown شامل کریں۔

`docusaurus.config.js` فائل میں ترمیم کریں:

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'docsVersionDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

Docs version dropdown آپ کے navbar میں ظاہر ہوتا ہے:

![Docs Version Dropdown](./img/docsVersionDropdown.png)

## موجودہ version کو update کریں

Versioned docs کو ان کے متعلقہ فولڈر میں edit کرنا ممکن ہے:

- `versioned_docs/version-1.0/hello.md` updates `http://localhost:3000/docs/hello`
- `docs/hello.md` updates `http://localhost:3000/docs/next/hello`
