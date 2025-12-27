---
sidebar_position: 5
---

# اپنی سائٹ کو Deploy کریں

Docusaurus ایک **static-site-generator** ہے (جسے **[Jamstack](https://jamstack.org/)** بھی کہا جاتا ہے)۔

یہ آپ کی سائٹ کو سادہ **static HTML، JavaScript اور CSS فائلوں** کے طور پر بناتا ہے۔

## اپنی سائٹ بنائیں

**Production** کے لیے اپنی سائٹ بنائیں:

```bash
npm run build
```

Static فائلیں `build` فولڈر میں بنتی ہیں۔

## اپنی سائٹ کو Deploy کریں

اپنی production build کو locally test کریں:

```bash
npm run serve
```

`build` فولڈر اب [http://localhost:3000/](http://localhost:3000/) پر serve ہو رہا ہے۔

اب آپ `build` فولڈر کو **تقریباً کہیں بھی** آسانی سے، **مفت** یا بہت کم قیمت میں deploy کر سکتے ہیں (**[Deployment Guide](https://docusaurus.io/docs/deployment)** پڑھیں)۔
