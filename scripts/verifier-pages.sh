#!/usr/bin/env bash
# Contrôles du site (étape tests de `socle ci`), bash 3.2 :
#   1. régénère les pages (python3 build.py) ;
#   2. échoue si `git status --porcelain` montre une page régénérée différente de l'index git
#      (sources changées sans régénération, ou page régénérée pas encore relue et indexée) ;
#   3. échoue en nommant chaque page attendue absente ;
#   4. échoue en nommant la page et le lien pour chaque lien interne cassé (href="/…" qui ne mène
#      ni à un fichier ni au index.html d'un dossier) ;
#   5. lance les tests du site (tests/ : HTML généré et cas d'échec de ce script).
# Seule la colonne « arbre de travail » de git status compte : une page indexée (git add) passe,
# ce qui permet de lancer `socle ci --all` avant le commit.
set -u
set -f   # pas d'expansion des jokers dans les chemins et les liens
cd "$(dirname "$0")/.." || exit 1

# URL publiques dont l'app et les stores ont besoin : un fichier par page.
PAGES_ATTENDUES="
index.html
404.html
cgu/index.html
confidentialite/index.html
en/terms/index.html
en/privacy/index.html
es/terminos/index.html
es/privacidad/index.html
mentions-legales/index.html
en/legal-notice/index.html
es/aviso-legal/index.html
suppression-compte/index.html
en/delete-account/index.html
es/eliminar-cuenta/index.html
contact/index.html
en/contact/index.html
es/contacto/index.html
"

echec=0

# build.py écrit une page par ligne, chemin relatif à la racine du dépôt.
if ! sorties=$(python3 build.py); then
  echo "✗ python3 build.py a échoué" >&2
  exit 1
fi

for f in $sorties; do
  ligne=$(git status --porcelain --untracked-files=all -- "$f")
  if [ -n "$ligne" ] && [ "${ligne:1:1}" != " " ]; then
    echo "✗ page pas à jour dans l'index git : $f (relis-la, puis git add)" >&2
    echec=1
  fi
done

for p in $PAGES_ATTENDUES; do
  if [ ! -f "$p" ]; then
    echo "✗ page attendue absente : $p" >&2
    echec=1
    continue
  fi
  for lien in $(grep -o 'href="/[^"]*"' "$p" | sed 's/^href="//; s/"$//'); do
    case "$lien" in //*) continue ;; esac   # lien externe sans schéma
    cible=${lien%%#*}
    cible=${cible#/}
    if [ -n "$cible" ] && [ -f "$cible" ]; then continue; fi
    if [ -f "${cible%/}/index.html" ] || { [ -z "$cible" ] && [ -f index.html ]; }; then continue; fi
    echo "✗ lien interne cassé : $p → $lien" >&2
    echec=1
  done
done

# VERIFIER_PAGES_SANS_TESTS : posé par tests/test_verifier.py, qui lance ce script sur une copie du site.
if [ -z "${VERIFIER_PAGES_SANS_TESTS:-}" ] && ! python3 -I -B -m unittest discover -s tests -q 2>&1; then
  echo "✗ tests du site (tests/)" >&2
  echec=1
fi

if [ "$echec" -eq 0 ]; then
  echo "✓ pages à jour, pages attendues présentes, liens internes valides, tests verts"
fi
exit "$echec"
