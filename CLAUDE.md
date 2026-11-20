# tvtimi-site

Site public de TvTimi (tvtimi.fr) : pages légales de l'app en fr, en, es, publiées par GitHub Pages.
Dépôt **public** : ni secret, ni code de l'app, ni adresse personnelle dans un commit (adresse « noreply » de
GitHub réglée dans la config locale du clone : ne pas la changer).

Profil : `.socle/projet.toml`
Process : skill `carte` du socle

## Commandes

- `python3 build.py` : régénère les pages HTML depuis `src/*.md` (sans dépendance).
- `bash scripts/verifier-pages.sh` (étape tests de `socle ci`) : pages régénérées identiques à l'index git, pages
  attendues présentes. Une page régénérée se relit puis s'indexe (`git add`) avant `socle ci --all`.

## Règles du projet

- Pages générées : `.claude/rules/pages-generees.md`.
- Texte légal changé : date de version en tête des six textes et `LegalDocuments.version` dans l'app TvTimi
  (dépôt privé), relus par Patrick avant toute mise en ligne.

## Où chercher

- `build.py` : routes par langue (`DOCS`), gabarit de page, pied de page.
- `src/` : textes source ; `style.css` ; `CNAME` (domaine de Pages) ; `index.html` et `404.html` écrits à la main.
