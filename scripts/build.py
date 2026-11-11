"""Copy only public website files; never package workspace attachments or docs."""

from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "portfolio-dist"
SOURCES = {
    "shared": "shared",
    "demo-ventilation": "ventilation",
    "demo-furniture": "furniture",
    "demo-autoservice": "autoservice",
    "portfolio-src": "",
}
PUBLIC_EXTENSIONS = {".html", ".css", ".js", ".svg"}


def build(include_prior_work=True):
    planned = {}
    for source, destination in SOURCES.items():
        for file in (ROOT / source).rglob("*"):
            if file.is_file() and file.suffix in PUBLIC_EXTENSIONS:
                target = DIST / destination / file.relative_to(ROOT / source)
                planned[target] = file
    expected = {file.resolve() for file in planned}
    for file in DIST.rglob("*"):
        if file.is_file() and file.resolve() not in expected and file.name != ".nojekyll":
            raise RuntimeError(f"Unexpected distribution file: {file}. Inspect it before rebuilding.")
    for target, source in planned.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".html":
            content = source.read_text(encoding="utf-8")
            content = content.replace("../portfolio-src/index.html", "../index.html")
            if source.parent.name == "portfolio-src":
                for name, destination in SOURCES.items():
                    if destination:
                        content = content.replace(f"../{name}/", f"{destination}/")
                if not include_prior_work:
                    before, section = content.split("<!-- PRIOR_WORK_START -->", 1)
                    _, after = section.split("<!-- PRIOR_WORK_END -->", 1)
                    content = before + after
            target.write_text(content, encoding="utf-8", newline="\n")
        else:
            shutil.copyfile(source, target)
    (DIST / ".nojekyll").touch()
    print(f"Built {len(planned)} website files into portfolio-dist/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--without-prior-work", action="store_true")
    build(include_prior_work=not parser.parse_args().without_prior_work)
