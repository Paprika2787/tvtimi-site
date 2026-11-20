# tvtimi-site

Site public de TvTimi (tvtimi.fr), publié par GitHub Pages, en fr, en, es : CGU, confidentialité, mentions
légales, suppression du compte, contact, plus l'accueil et la 404.
Dépôt **public** : ni secret, ni code de l'app, ni adresse personnelle dans un commit (adresse « noreply » de
GitHub réglée dans la config locale du clone : ne pas la changer).

Profil : `.socle/projet.toml`
Process : skill `carte` du socle

## Commandes

- `python3 build.py` : régénère toutes les pages HTML depuis `src/*.md` (sans dépendance).
- `bash scripts/verifier-pages.sh` (étape tests de `socle ci`) : pages régénérées identiques à l'index git, pages
  attendues présentes, liens internes valides, puis `tests/` (HTML généré ; cas d'échec du script, rejoués sur
  une copie). Une page régénérée se relit puis s'indexe (`git add`) avant `socle ci --all`.

## Règles du projet

- Pages générées : `.claude/rules/pages-generees.md`.
- Texte légal changé (CGU ou confidentialité) : date de version en tête des six textes et `LegalDocuments.version`
  dans l'app TvTimi (dépôt privé), relus par Patrick avant toute mise en ligne.
- Éditeur, hébergeur et contact : table `[legal]` du profil ; les sources les citent par `{editeur}`,
  `{hebergeur}` (hébergeur du site seul) et `{contact}`, sauf les CGU et la politique (versionnées, valeurs
  écrites à la main) ; détail dans la règle des pages générées.

## Où chercher

- `build.py` : sortes de page et chemins par langue (`PAGES`), gabarit, sélecteur de langue, pied de page.
- `src/` : textes source ; `tests/test_pages.py` ; `style.css` ; `CNAME` (domaine de Pages).
