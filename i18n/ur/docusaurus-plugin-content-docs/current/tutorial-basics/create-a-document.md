---
sidebar_position: 2
---

# ایک Document بنائیں

Documents **صفحات کے گروپس** ہیں جو مربوط ہیں:

- ایک **sidebar**
- **previous/next navigation**
- **versioning**

## اپنا پہلا Doc بنائیں

`docs/hello.md` پر ایک Markdown فائل بنائیں:

```md title="docs/hello.md"
# Hello

This is my **first Docusaurus document**!
```

ایک نیا document اب [http://localhost:3000/docs/hello](http://localhost:3000/docs/hello) پر دستیاب ہے۔

## Sidebar کو Configure کریں

Docusaurus خودکار طور پر `docs` فولڈر سے **ایک sidebar بناتا ہے**۔

Sidebar کے label اور position کو customize کرنے کے لیے metadata شامل کریں:

```md title="docs/hello.md" {1-4}
---
sidebar_label: 'Hi!'
sidebar_position: 3
---

# Hello

This is my **first Docusaurus document**!
```

`sidebars.js` میں اپنا sidebar واضح طور پر بنانا بھی ممکن ہے:

```js title="sidebars.js"
export default {
  tutorialSidebar: [
    'intro',
    // highlight-next-line
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
};
```
