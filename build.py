#!/usr/bin/env python3
"""Static site generator: converts Markdown files to styled HTML pages."""

import os
import sys
import shutil
import re
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Installing python-markdown...")
    os.system(f"{sys.executable} -m pip install markdown pymdown-extensions")
    import markdown

SITE_DIR = Path("site")
CONTENT_DIR = Path("content")
TEMPLATES_DIR = Path("templates")


def read_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def collect_pages(content_dir: Path) -> list[dict]:
    pages = []
    for md_file in sorted(content_dir.rglob("*.md")):
        rel = md_file.relative_to(content_dir)
        html_rel = rel.with_suffix(".html")
        text = md_file.read_text(encoding="utf-8")
        title_match = re.match(r"^#\s+(.+)", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else title_from_filename(md_file)
        pages.append({
            "md_path": md_file,
            "html_rel": html_rel,
            "title": title,
            "content": text,
        })
    return pages


def build_sidebar(pages: list[dict], current_rel: Path, root: str) -> str:
    links = []
    for p in pages:
        cls = ' class="active"' if p["html_rel"] == current_rel else ""
        label = "Home" if p["html_rel"] == Path("index.html") else p["title"]
        links.append(f'<li><a href="{root}{p["html_rel"]}"{cls}>{label}</a></li>')
    return "\n          ".join(links)


def build():
    md_ext = markdown.Markdown(
        extensions=["codehilite", "fenced_code", "tables", "toc", "smarty", "attr_list"],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": True},
            "toc": {"permalink": True},
        },
    )

    template = read_template("base.html")

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Copy static assets from templates
    for asset in ("style.css", "highlight.css", "theme.js"):
        shutil.copy2(TEMPLATES_DIR / asset, SITE_DIR / asset)

    if not CONTENT_DIR.exists():
        CONTENT_DIR.mkdir(parents=True)
        (CONTENT_DIR / "index.md").write_text(
            "# CUBRID Code Analysis\n\n"
            "Welcome! Add your analysis markdown files to the `content/` directory and run `python build.py`.\n\n"
            "## Getting Started\n\n"
            "1. Put `.md` files in `content/`\n"
            "2. Run `python build.py`\n"
            "3. Serve with `python -m http.server -d site 8000`\n",
            encoding="utf-8",
        )

    pages = collect_pages(CONTENT_DIR)
    if not pages:
        print("No .md files found in content/")
        return

    for page in pages:
        md_ext.reset()
        html_content = md_ext.convert(page["content"])

        depth = len(page["html_rel"].parts) - 1
        root = "../" * depth if depth > 0 else ""

        sidebar = build_sidebar(pages, page["html_rel"], root)
        html = template.format(
            title=page["title"],
            content=html_content,
            sidebar_links=sidebar,
            root=root,
        )

        out_path = SITE_DIR / page["html_rel"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"  {page['md_path']} -> {out_path}")

    # Copy any images/assets from content
    for f in CONTENT_DIR.rglob("*"):
        if f.is_file() and f.suffix.lower() not in (".md",):
            dest = SITE_DIR / f.relative_to(CONTENT_DIR)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            print(f"  [asset] {f} -> {dest}")

    print(f"\nBuilt {len(pages)} page(s) in {SITE_DIR}/")
    print(f"Serve with: python -m http.server -d site 8000")


if __name__ == "__main__":
    build()
