"""Genere les pages de tvtimi.fr depuis src/*.md (titres, paragraphes,
listes, liens). Sans dependance : python3 build.py."""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
DOCS = {
    # langue : (chemin CGU, chemin confidentialite, libelles)
    "fr": ("/cgu", "/confidentialite",
           {"terms": "Conditions d'utilisation",
            "privacy": "Politique de confidentialité", "lang": "Langue"}),
    "en": ("/en/terms", "/en/privacy",
           {"terms": "Terms of use", "privacy": "Privacy policy",
            "lang": "Language"}),
    "es": ("/es/terminos", "/es/privacidad",
           {"terms": "Condiciones de uso", "privacy": "Política de privacidad",
            "lang": "Idioma"}),
}


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
                 out)
    return out.replace("contact@tvtimi.fr",
                       '<a href="mailto:contact@tvtimi.fr">contact@tvtimi.fr</a>')


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


def page(lang: str, kind: str, title: str, body: str) -> str:
    terms, privacy, labels = DOCS[lang]
    switch = " ".join(
        f'<a href="{DOCS[other][0 if kind == "terms" else 1]}" hreflang="{other}"'
        f'{" aria-current=\"page\"" if other == lang else ""}>{other.upper()}</a>'
        for other in DOCS)
    other_doc = (privacy, labels["privacy"]) if kind == "terms" else (terms, labels["terms"])
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header><a class="brand" href="/">TvTimi</a><nav aria-label="{labels['lang']}">{switch}</nav></header>
<main>
{body}
</main>
<footer><a href="{other_doc[0]}">{other_doc[1]}</a> · <a href="mailto:contact@tvtimi.fr">contact@tvtimi.fr</a></footer>
</body>
</html>
"""


for lang, (terms, privacy, _) in DOCS.items():
    for kind, path in (("terms", terms), ("privacy", privacy)):
        title, body = to_html((ROOT / "src" / f"{kind}-{lang}.md").read_text())
        out = ROOT / path.lstrip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, kind, title, body))
        print(out.relative_to(ROOT))
