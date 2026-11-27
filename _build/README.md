# How this website is built

The published `.html` pages in the website folder are **generated**. Edit the sources here, then rebuild.

```
python _build/build.py
```

| What you want to change | Edit this |
|---|---|
| A page's text, photos or SEO title/description | `_build/pages/<page>.html` (front matter at the top) |
| Menu, top bar, footer, WhatsApp button | `_build/partials/header.html`, `_build/partials/footer.html` |
| Annual reports / IT reports lists | `_build/reports.json` |
| Organisation details for Google | `_build/partials/org.jsonld` |
| Styles / behaviour | `assets/css/site.css`, `assets/js/site.js` |

The build also regenerates `sitemap.xml` (with image entries) and warns about missing files or broken page links.

## Adding an IT report or annual report

1. Copy the PDF into `reports/it/` (or `reports/annual/`), e.g. `reports/it/itr-ay-2024-25.pdf`.
2. Add an entry at the top of the right list in `_build/reports.json`:
   ```json
   {"title": "Income Tax Return acknowledgement", "period": "AY 2024–25", "file": "reports/it/itr-ay-2024-25.pdf"}
   ```
3. Run `python _build/build.py`, then commit and push.

Folders starting with `_` are not published by GitHub Pages.
