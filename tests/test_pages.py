"""Contrôles du HTML généré par build.py (lancés par scripts/verifier-pages.sh).

Les chemins attendus sont écrits ici, indépendamment de build.py : ce sont les URL
de l'app et des fiches des stores. Bibliothèque standard seulement.
"""
import re
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LANGUES = ("fr", "en", "es")

# Sorte de page -> chemin par langue (carte « Site — pages exigées par les stores et la loi »).
CHEMINS = {
    "terms": {"fr": "/cgu", "en": "/en/terms", "es": "/es/terminos"},
    "privacy": {"fr": "/confidentialite", "en": "/en/privacy", "es": "/es/privacidad"},
    "legal-notice": {"fr": "/mentions-legales", "en": "/en/legal-notice", "es": "/es/aviso-legal"},
    "delete-account": {"fr": "/suppression-compte", "en": "/en/delete-account",
                       "es": "/es/eliminar-cuenta"},
    "contact": {"fr": "/contact", "en": "/en/contact", "es": "/es/contacto"},
}
SOURCE_HEBERGEUR = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"


class Page(HTMLParser):
    """Titre, liens, liens du pied de page, sélecteur de langue et texte d'une page."""

    def __init__(self, chemin: Path):
        super().__init__()
        self.titre, self.liens, self.pied, self.selecteur = "", [], [], []
        self._dans = {"title": False, "footer": False, "header": False}
        self._texte = []
        self.brut = chemin.read_text(encoding="utf-8")
        self.feed(self.brut)
        self.texte = re.sub(r"\s+", " ", "".join(self._texte))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self._dans:
            self._dans[tag] = True
        if tag == "a" and "href" in a:
            self.liens.append(a["href"])
            if self._dans["footer"]:
                self.pied.append(a["href"])
            if self._dans["header"] and "hreflang" in a:
                self.selecteur.append((a["href"], a["hreflang"], a.get("aria-current")))

    def handle_endtag(self, tag):
        if tag in self._dans:
            self._dans[tag] = False

    def handle_data(self, data):
        if self._dans["title"]:
            self.titre += data
        self._texte.append(data)


def fichier(url: str) -> Path:
    return RACINE / url.lstrip("/") / "index.html"


def page(sorte: str, langue: str) -> Page:
    return Page(fichier(CHEMINS[sorte][langue]))


def toutes_les_pages():
    """(langue du pied de page, Page) pour les 17 pages attendues."""
    yield "fr", Page(RACINE / "index.html")
    yield "fr", Page(RACINE / "404.html")
    for sorte in CHEMINS:
        for langue in LANGUES:
            yield langue, page(sorte, langue)


class TestAccueil(unittest.TestCase):
    def test_accueil_lie_quinze_pages(self):  # RG1
        liens = set(Page(RACINE / "index.html").liens)
        attendus = {CHEMINS[s][l] for s in CHEMINS for l in LANGUES}
        self.assertEqual(len(attendus), 15)
        self.assertLessEqual(attendus, liens, sorted(attendus - liens))

    def test_titres(self):
        self.assertEqual(Page(RACINE / "index.html").titre, "TvTimi")
        self.assertEqual(Page(RACINE / "404.html").titre, "Page introuvable · TvTimi")
        for sorte in CHEMINS:
            for langue in LANGUES:
                with self.subTest(sorte=sorte, langue=langue):
                    self.assertTrue(page(sorte, langue).titre.endswith(" · TvTimi"))


class TestGabarit(unittest.TestCase):
    def test_pied_de_page(self):  # RG11
        for langue, p in toutes_les_pages():
            attendus = [CHEMINS[s][langue] for s in CHEMINS]
            with self.subTest(titre=p.titre):
                self.assertEqual(p.pied, attendus)

    def test_selecteur_langue(self):  # RG10
        for sorte in CHEMINS:
            for langue in LANGUES:
                with self.subTest(sorte=sorte, langue=langue):
                    attendus = [(CHEMINS[sorte][l], l, "page" if l == langue else None)
                                for l in LANGUES]
                    self.assertEqual(page(sorte, langue).selecteur, attendus)

    def test_seule_adresse_email(self):  # RG3
        adresses = set()
        for _, p in toutes_les_pages():
            adresses |= set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", p.brut))
        self.assertEqual(adresses, {"contact@tvtimi.fr"})

    def test_url_de_l_app(self):  # RG14
        for url in ("/cgu", "/confidentialite", "/en/terms", "/en/privacy",
                    "/es/terminos", "/es/privacidad"):
            with self.subTest(url=url):
                self.assertTrue(fichier(url).is_file())


class TestMentionsLegales(unittest.TestCase):
    PAYS = {"fr": "États-Unis", "en": "United States", "es": "Estados Unidos"}

    def test_mentions_legales(self):  # RG2
        for langue in LANGUES:
            p = page("legal-notice", langue)
            with self.subTest(langue=langue):
                for attendu in ("P.Dev", "1-1", "GitHub, Inc., 88 Colin P. Kelly Jr. Street, "
                                "San Francisco, CA 94107", self.PAYS[langue], "Supabase Pte. Ltd., 65 Chulia Street",
                                "contact@tvtimi.fr"):
                    self.assertIn(attendu, p.texte)
                self.assertIn(SOURCE_HEBERGEUR, p.liens)
                self.assertIn("mailto:contact@tvtimi.fr", p.liens)
                self.assertNotRegex(p.texte.lower(), r"directeur|director")
                self.assertNotRegex(p.texte.lower(), r"t[ée]l[ée]phone|phone|tel[ée]fono|t[ée]l\.")
                self.assertNotRegex(p.texte, r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")
                self.assertNotRegex(p.texte, r"(?:\+33\s?|0)[1-9](?:[ .-]?\d{2}){4}")

    def test_legal_profil_dans_page(self):  # RG16
        legal = tomllib.loads((RACINE / ".socle/projet.toml").read_text(encoding="utf-8"))["legal"]
        self.assertEqual(legal["editeur"], "P.Dev")
        self.assertEqual(legal["contact"], "contact@tvtimi.fr")
        for langue in LANGUES:
            with self.subTest(langue=langue):
                texte = page("legal-notice", langue).texte
                for cle in ("editeur", "contact", "hebergeur"):
                    self.assertIn(legal[cle], texte)


class TestSuppression(unittest.TestCase):
    # Libellés de l'écran Profil et de la confirmation de suppression de l'app (dépôt privé).
    LIBELLES = {
        "fr": ("Profil", "Supprimer mon compte", "SUPPRIMER", "Supprimer définitivement"),
        "en": ("Profile", "Delete my account", "DELETE", "Delete permanently"),
        "es": ("Perfil", "Eliminar mi cuenta", "ELIMINAR", "Eliminar definitivamente"),
    }
    SANS_APP = {
        "fr": ("adresse e-mail de ton compte", "dans un nouveau message",
               "n'est supprimé qu'après ta réponse", "sous un mois"),
        "en": ("email address of your account", "in a new message",
               "only deleted after your reply", "within one month"),
        "es": ("dirección de correo electrónico de tu cuenta", "en un mensaje nuevo",
               "solo se elimina después de tu respuesta", "en el plazo de un mes"),
    }
    # Les quatre puces de « Ce qui est supprimé », en entier ; celle du suivi est la phrase de la politique.
    DONNEES = {
        "fr": ("Ton compte : ton adresse e-mail, ton mot de passe, la langue de l'application au moment de "
               "l'inscription, et ton prénom si tu l'as indiqué.",
               "Ton suivi : les œuvres de ta bibliothèque et leur statut, les épisodes marqués comme vus, "
               "tes notes par épisode et par œuvre.",
               "Ton accord aux conditions : la version des conditions d'utilisation et de la politique de "
               "confidentialité que tu as acceptée, avec la date.",
               "Les journaux techniques liés à ton compte."),
        "en": ("Your account: your email address, your password, the app language when you signed up, and "
               "your first name if you added it.",
               "Your tracking: the shows in your library and their status, the episodes marked as watched, "
               "your ratings per episode and per show.",
               "Your agreement to the terms: the version of the terms of use and of the privacy policy that "
               "you accepted, with the date.",
               "The technical logs linked to your account."),
        "es": ("Tu cuenta: tu dirección de correo electrónico, tu contraseña, el idioma de la aplicación en el "
               "momento del registro y tu nombre si lo indicaste.",
               "Tu seguimiento: las obras de tu biblioteca y su estado, los episodios marcados como vistos, "
               "tus notas por episodio y por obra.",
               "Tu aceptación de las condiciones: la versión de las condiciones de uso y de la política de "
               "privacidad que aceptaste, con la fecha.",
               "Los registros técnicos vinculados a tu cuenta."),
    }
    DELAI = {
        "fr": ("effacées immédiatement et définitivement", "90 jours", "30 jours"),
        "en": ("erased immediately and permanently", "90 days", "30 days"),
        "es": ("se borran de inmediato y de forma definitiva", "90 días", "30 días"),
    }

    def test_suppression_libelles_app(self):  # RG4
        for langue, (profil, entree, mot, bouton) in self.LIBELLES.items():
            with self.subTest(langue=langue):
                texte = page("delete-account", langue).texte
                self.assertIn(f"{profil}, {entree}", texte)
                self.assertIn(mot, texte)
                self.assertIn(bouton, texte)

    def test_suppression_demande_sans_app(self):  # RG5
        for langue, phrases in self.SANS_APP.items():
            with self.subTest(langue=langue):
                p = page("delete-account", langue)
                self.assertIn("mailto:contact@tvtimi.fr", p.liens)
                for phrase in phrases:
                    self.assertIn(phrase, p.texte)

    def test_suppression_donnees(self):  # RG6
        for langue, puces in self.DONNEES.items():
            with self.subTest(langue=langue):
                texte = page("delete-account", langue).texte
                for puce in puces:
                    self.assertIn(puce, texte)
                self.assertIn(puces[1], page("privacy", langue).texte)

    def test_suppression_delai(self):  # RG7
        for langue, (formule, journaux, refuse) in self.DELAI.items():
            with self.subTest(langue=langue):
                texte = page("delete-account", langue).texte
                self.assertIn(formule, texte)
                self.assertIn(journaux, texte)
                self.assertNotIn(refuse, texte)


class TestContact(unittest.TestCase):
    def test_contact_mailto(self):  # RG9
        for langue in LANGUES:
            with self.subTest(langue=langue):
                p = page("contact", langue)
                self.assertIn("mailto:contact@tvtimi.fr", p.liens)
                self.assertIn("contact@tvtimi.fr", p.texte)


if __name__ == "__main__":
    unittest.main()
