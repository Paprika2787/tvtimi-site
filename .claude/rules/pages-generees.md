---
paths:
  - "build.py"
  - "src/**"
  - "index.html"
  - "404.html"
  - "cgu/**"
  - "confidentialite/**"
  - "mentions-legales/**"
  - "suppression-compte/**"
  - "contact/**"
  - "en/**"
  - "es/**"
  - "scripts/verifier-pages.sh"
  - "tests/**"
  - "_config.yml"
---

# Pages générées

- Toutes les pages HTML (accueil et 404 comprises) sortent de `python3 build.py` : on modifie `src/*.md` ou
  `build.py`, jamais la page HTML à la main (la prochaine régénération l'écraserait, et `verifier-pages.sh` la
  signale).
- Le chemin d'une page est une URL de l'app et des fiches des stores : il ne change pas. Une page ajoutée entre
  dans `PAGES` de `build.py`, dans `PAGES_ATTENDUES` de `scripts/verifier-pages.sh` et dans `CHEMINS` de
  `tests/test_pages.py`.
- Éditeur, hébergeur, contact : jamais écrits en dur dans les sources des pages du site, toujours `{editeur}`,
  `{hebergeur}`, `{contact}` (valeurs de `[legal]` du profil). Exception : `src/terms-*.md` et
  `src/privacy-*.md`, textes versionnés acceptés dans l'app ; leurs valeurs se changent à la main, avec la date
  de version et `LegalDocuments.version`. `{hebergeur}` ne désigne que l'hébergeur du site (GitHub) : l'hébergeur
  des données de l'app (Supabase) et le paragraphe sur les adresses IP s'écrivent à la main dans
  `src/legal-notice-*.md`, et changent avec `hebergeur`.
- Publication : `_config.yml` exclut de GitHub Pages tout ce qui n'est pas le site ; un fichier ajouté hors
  des pages (source, outil, note) y entre.
- Page de suppression : délai et données repris mot pour mot de la politique de confidentialité ; libellés de l'app
  recopiés de ses fichiers de traduction (dépôt privé) et vérifiés par `tests/test_pages.py`.
