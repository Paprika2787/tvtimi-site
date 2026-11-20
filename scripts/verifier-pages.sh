#!/usr/bin/env bash
# Contrôles du site (étape tests de `socle ci`), bash 3.2 :
#   1. régénère les pages (python3 build.py) ;
#   2. échoue si `git status --porcelain` montre une page régénérée différente de l'index git
#      (sources changées sans régénération, ou page régénérée pas encore relue et indexée) ;
#   3. échoue en nommant chaque page attendue absente.
# Seule la colonne « arbre de travail » de git status compte : une page indexée (git add) passe,
# ce qui permet de lancer `socle ci --all` avant le commit.
set -u
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
  fi
done

if [ "$echec" -eq 0 ]; then
  echo "✓ pages à jour et pages attendues présentes"
fi
exit "$echec"
