"""Check deployable HTML and asset links without external dependencies."""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html", "ventilation/index.html", "furniture/index.html",
    "furniture/services.html", "furniture/portfolio.html",
    "furniture/contacts.html", "autoservice/index.html",
)
NOTICE = "Демонстрационный проект. Не является сайтом действующей компании"
ALLOWED_EXTERNAL = {"https://msk.etln-rcw.ru/", "https://new.etln-rcw.ru/"}


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        node = dict(attrs)
        self.nodes.append((tag, node))
        if "id" in node:
            self.ids.append(node["id"])


def validate(root):
    failures = []
    documents = {}
    for name in PAGES:
        file = root / name
        if not file.is_file():
            failures.append(f"Missing page: {name}")
            continue
        content = file.read_text(encoding="utf-8")
        doc = Document()
        doc.feed(content)
        documents[file.resolve()] = doc
        checks = {
            "demo notice": NOTICE in content,
            "one h1": sum(tag == "h1" for tag, _ in doc.nodes) == 1,
            "title": bool(re.search(r"<title>[^<]+</title>", content)),
            "description": any(tag == "meta" and a.get("name") == "description" and a.get("content") for tag, a in doc.nodes),
            "viewport": any(tag == "meta" and a.get("name") == "viewport" for tag, a in doc.nodes),
            "favicon": any(tag == "link" and a.get("rel") == "icon" for tag, a in doc.nodes),
            "unique ids": len(doc.ids) == len(set(doc.ids)),
            "no forms": all(tag not in ("form", "input", "textarea", "iframe") for tag, _ in doc.nodes),
            "no inline event handlers": all(not key.startswith("on") for _, a in doc.nodes for key in a),
            "all image alternatives": all("alt" in a and "width" in a and "height" in a for tag, a in doc.nodes if tag == "img"),
        }
        for check, passed in checks.items():
            if not passed:
                failures.append(f"{name}: {check}")

    for file, doc in documents.items():
        for tag, attrs in doc.nodes:
            for attr in ("href", "src"):
                value = attrs.get(attr)
                if value is None:
                    continue
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    if tag != "a" or value not in ALLOWED_EXTERNAL:
                        failures.append(f"{file.name}: unexpected external URL {value}")
                    continue
                if value.startswith("/") or not value:
                    failures.append(f"{file.name}: non-relative/empty URL {value}")
                    continue
                target = (file.parent / unquote(url.path)).resolve() if url.path else file
                if target.is_dir():
                    target /= "index.html"
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    failures.append(f"{file.relative_to(root)}: broken link {value}")
                elif url.fragment:
                    target_doc = documents.get(target)
                    if target_doc is None or unquote(url.fragment) not in target_doc.ids:
                        failures.append(f"{file.relative_to(root)}: missing fragment {value}")

    for file in root.rglob("*.css"):
        for url in re.findall(r"url\([\"']?([^\)\"']+)", file.read_text(encoding="utf-8")):
            if not (file.parent / url).is_file():
                failures.append(f"{file.name}: unresolved CSS asset {url}")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"Static QA: {len(documents)}/{len(PAGES)} pages; {len(failures)} failures")
    return not failures


if __name__ == "__main__":
    sys.exit(0 if validate(ROOT / "portfolio-dist") else 1)
