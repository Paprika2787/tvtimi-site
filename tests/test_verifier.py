"""Cas d'échec de scripts/verifier-pages.sh, rejoués sur une copie du site.

Chaque test copie les fichiers du dépôt (suivis et non ignorés) dans un dossier
temporaire, y crée un dépôt git avec tout indexé, provoque un écart, puis lance le
script avec VERIFIER_PAGES_SANS_TESTS=1 (sans quoi il relancerait ces tests).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Un hook git exporte GIT_DIR (chemin absolu dans un worktree) : sans ce filtre, les commandes
# git de la copie viseraient le vrai dépôt et écriraient dans son index.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(dossier: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=dossier, env=ENV, check=True,
                          capture_output=True, text=True).stdout


class TestVerifierPages(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.site = Path(self._tmp.name) / "site"
        fichiers = _git(RACINE, "ls-files", "-co", "--exclude-standard", "-z").split("\0")
        for relatif in filter(None, fichiers):
            source = RACINE / relatif
            if source.is_file():
                cible = self.site / relatif
                cible.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, cible)
        _git(self.site, "init", "-q")
        self.regenerer_et_indexer()

    def regenerer_et_indexer(self) -> None:
        subprocess.run(["python3", "build.py"], cwd=self.site, env=ENV, check=True,
                       capture_output=True)
        _git(self.site, "add", "-A")

    def tearDown(self):
        self._tmp.cleanup()

    def lancer(self) -> subprocess.CompletedProcess:
        env = dict(ENV, VERIFIER_PAGES_SANS_TESTS="1")
        return subprocess.run(["bash", "scripts/verifier-pages.sh"], cwd=self.site, env=env,
                              capture_output=True, text=True)

    def remplacer(self, relatif: str, avant: str, apres: str) -> None:
        chemin = self.site / relatif
        texte = chemin.read_text(encoding="utf-8")
        self.assertIn(avant, texte)
        chemin.write_text(texte.replace(avant, apres), encoding="utf-8")

    def test_copie_intacte_verte(self):
        resultat = self.lancer()
        self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_lien_interne_casse(self):  # RG13
        self.remplacer("build.py", '"<h1>TvTimi</h1>"', '"<h1><a href=\\"/contactt\\">TvTimi</a></h1>"')
        self.regenerer_et_indexer()  # seul le lien cassé reste en écart
        resultat = self.lancer()
        self.assertEqual(resultat.returncode, 1)
        self.assertIn("lien interne cassé : index.html → /contactt", resultat.stderr)
        self.assertNotIn("page pas à jour", resultat.stderr)

    def test_page_modifiee_a_la_main_puis_indexee(self):  # RG10
        self.remplacer("mentions-legales/index.html", "<h1>Mentions légales</h1>", "<h1>Modifiée</h1>")
        _git(self.site, "add", "mentions-legales/index.html")
        resultat = self.lancer()
        self.assertEqual(resultat.returncode, 1)
        self.assertIn("page pas à jour dans l'index git : mentions-legales/index.html", resultat.stderr)

    def test_page_attendue_absente(self):  # RG12
        self.remplacer("build.py", '("/contact", "Contact")', '("/contact-retire", "Contact")')
        (self.site / "contact" / "index.html").unlink()
        self.regenerer_et_indexer()  # seule la page absente reste en écart
        resultat = self.lancer()
        self.assertEqual(resultat.returncode, 1)
        self.assertIn("page attendue absente : contact/index.html", resultat.stderr)
        self.assertNotIn("page pas à jour", resultat.stderr)


if __name__ == "__main__":
    unittest.main()
