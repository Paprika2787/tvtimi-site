---
paths:
  - "build.py"
  - "src/**"
  - "cgu/**"
  - "confidentialite/**"
  - "en/**"
  - "es/**"
  - "scripts/verifier-pages.sh"
---

# Pages générées

- Les `*/index.html` des pages légales sortent de `python3 build.py` : on modifie `src/*.md` ou `build.py`, jamais
  la page HTML à la main (la prochaine régénération l'écraserait, et `verifier-pages.sh` la signale).
- Le chemin d'une page est une URL de l'app et des fiches des stores : il ne change pas. Une page ajoutée entre
  dans `PAGES_ATTENDUES` de `scripts/verifier-pages.sh`.
