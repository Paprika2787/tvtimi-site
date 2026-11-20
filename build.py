"""Genere les pages de tvtimi.fr depuis src/*.md (titres, paragraphes,
listes, liens), plus l'accueil et la page 404. Sans dependance : python3 build.py.

Les marqueurs {editeur}, {hebergeur} et {contact} des sources sont remplaces par
les valeurs de la table [legal] de .socle/projet.toml (une seule source)."""
import html
import pathlib
import re
import tomllib

ROOT = pathlib.Path(__file__).parent
LANGS = ("fr", "en", "es")
LANG_NAMES = {"fr": "Français", "en": "English", "es": "Español"}

# Sorte de page -> langue -> (chemin, libelle). Les chemins sont des URL de l'app
# et des fiches des stores : ils ne changent pas.
PAGES = {
    "terms": {
        "fr": ("/cgu", "Conditions d'utilisation"),
        "en": ("/en/terms", "Terms of use"),
        "es": ("/es/terminos", "Condiciones de uso"),
    },
    "privacy": {
        "fr": ("/confidentialite", "Politique de confidentialité"),
        "en": ("/en/privacy", "Privacy policy"),
        "es": ("/es/privacidad", "Política de privacidad"),
    },
    "legal-notice": {
        "fr": ("/mentions-legales", "Mentions légales"),
        "en": ("/en/legal-notice", "Legal notice"),
        "es": ("/es/aviso-legal", "Aviso legal"),
    },
    "delete-account": {
        "fr": ("/suppression-compte", "Suppression du compte"),
        "en": ("/en/delete-account", "Account deletion"),
        "es": ("/es/eliminar-cuenta", "Eliminación de la cuenta"),
    },
    "contact": {
        "fr": ("/contact", "Contact"),
        "en": ("/en/contact", "Contact"),
        "es": ("/es/contacto", "Contacto"),
    },
}
LABELS = {
    "fr": {"lang": "Langue", "site": "Pages du site"},
    "en": {"lang": "Language", "site": "Site pages"},
    "es": {"lang": "Idioma", "site": "Páginas del sitio"},
}
TAGLINE = "Suis tes séries et animés, épisode par épisode. Bientôt sur iOS et Android."
LEGAL = tomllib.loads((ROOT / ".socle" / "projet.toml").read_text(encoding="utf-8"))["legal"]


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
                 out)
    contact = html.escape(LEGAL["contact"])
    return out.replace(contact, f'<a href="mailto:{contact}">{contact}</a>')


def to_html(markdown: str) -> tuple[str, str]:
    title, parts, items = "", [], []

    def flush():
        if items:
            parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    for block in markdown.strip().split("\n\n"):
        lines = block.strip().splitlines()
        if lines[0].startswith("# "):
            flush(); title = lines[0][2:].strip()
            parts.append(f"<h1>{html.escape(title)}</h1>")
        elif lines[0].startswith("## "):
            flush(); parts.append(f"<h2>{inline(lines[0][3:].strip())}</h2>")
        elif all(l.startswith("- ") for l in lines):
            items.extend(inline(l[2:]) for l in lines); flush()
        else:
            flush(); parts.append(f"<p>{inline(' '.join(lines))}</p>")
    flush()
    return title, "\n".join(parts)


def substitute(markdown: str) -> str:
    for key in ("editeur", "hebergeur", "contact"):
        markdown = markdown.replace("{" + key + "}", LEGAL[key])
    return markdown


def footer(lang: str) -> str:
    links = " · ".join(f'<a href="{PAGES[kind][lang][0]}">{PAGES[kind][lang][1]}</a>'
                       for kind in PAGES)
    return f'<footer><nav aria-label="{LABELS[lang]["site"]}">{links}</nav></footer>'


def switch(lang: str, kind: str) -> str:
    links = " ".join(
        f'<a href="{PAGES[kind][other][0]}" hreflang="{other}"'
        f'{" aria-current=\"page\"" if other == lang else ""}>{other.upper()}</a>'
        for other in LANGS)
    return f'<nav aria-label="{LABELS[lang]["lang"]}">{links}</nav>'


def document(lang: str, title: str, body: str, nav: str = "") -> str:
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header><a class="brand" href="/">TvTimi</a>{nav}</header>
<main>
{body}
</main>
{footer(lang)}
</body>
</html>
"""


def home_body(intro: str) -> str:
    parts = ["<h1>TvTimi</h1>", f"<p>{html.escape(intro)}</p>"]
    for lang in LANGS:
        attr = "" if lang == "fr" else f' lang="{lang}"'
        items = "".join(f'<li><a href="{PAGES[kind][lang][0]}">{PAGES[kind][lang][1]}</a></li>'
                        for kind in PAGES)
        parts.append(f"<h2{attr}>{LANG_NAMES[lang]}</h2>")
        parts.append(f"<ul{attr}>{items}</ul>")
    return "\n".join(parts)


def write(relative: str, content: str) -> None:
    out = ROOT / relative
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(relative)


write("index.html", document("fr", "TvTimi", home_body(TAGLINE)))
write("404.html", document("fr", "Page introuvable · TvTimi",
                           home_body(f"Page introuvable. {TAGLINE}")))
for kind, langs in PAGES.items():
    for lang, (path, label) in langs.items():
        source = (ROOT / "src" / f"{kind}-{lang}.md").read_text(encoding="utf-8")
        _, body = to_html(substitute(source))
        write(path.lstrip("/") + "/index.html",
              document(lang, f"{label} · TvTimi", body, switch(lang, kind)))
