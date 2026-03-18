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
TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - CUBRID Code Analysis</title>
  <link rel="stylesheet" href="{root}style.css">
  <link rel="stylesheet" href="{root}highlight.css">
</head>
<body>
  <nav>
    <a href="{root}index.html" class="logo">CUBRID Code Analysis</a>
    <button class="sidebar-toggle" onclick="document.body.classList.toggle('sidebar-open')" aria-label="Toggle sidebar">&#9776;</button>
  </nav>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-section">
        <h3>Pages</h3>
        <ul>
          {sidebar_links}
        </ul>
      </div>
    </aside>
    <main>
      <article>
        {content}
      </article>
    </main>
  </div>
  <footer>
    <p>CUBRID Code Analysis &mdash; Generated with a custom static site builder</p>
  </footer>
</body>
</html>
"""

CSS = """\
:root {
  --bg: #ffffff;
  --bg-alt: #f6f8fa;
  --fg: #1f2328;
  --fg-muted: #636c76;
  --accent: #0969da;
  --border: #d0d7de;
  --code-bg: #f6f8fa;
  --nav-bg: #24292f;
  --nav-fg: #ffffff;
  --max-width: 860px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --bg-alt: #161b22;
    --fg: #e6edf3;
    --fg-muted: #8b949e;
    --accent: #58a6ff;
    --border: #30363d;
    --code-bg: #161b22;
    --nav-bg: #010409;
    --nav-fg: #e6edf3;
  }
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

nav {
  background: var(--nav-bg);
  color: var(--nav-fg);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  position: sticky;
  top: 0;
  z-index: 100;
}

nav .logo {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--nav-fg);
  text-decoration: none;
}

nav a {
  color: var(--nav-fg);
  text-decoration: none;
  opacity: 0.8;
  font-size: 0.9rem;
}

nav a:hover { opacity: 1; }

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--nav-fg);
  font-size: 1.4rem;
  cursor: pointer;
  margin-left: auto;
  padding: 0.2rem 0.5rem;
}

.layout {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.sidebar {
  width: 240px;
  min-width: 240px;
  padding: 1.5rem 1rem;
  border-right: 1px solid var(--border);
  background: var(--bg-alt);
  position: sticky;
  top: 49px;
  height: calc(100vh - 49px);
  overflow-y: auto;
}

.sidebar h3 {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  margin-bottom: 0.5rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li { margin: 0; }

.sidebar a {
  display: block;
  padding: 0.35rem 0.5rem;
  color: var(--fg);
  text-decoration: none;
  font-size: 0.875rem;
  border-radius: 4px;
}

.sidebar a:hover { background: var(--border); }
.sidebar a.active { background: var(--accent); color: #fff; font-weight: 600; }

main {
  max-width: var(--max-width);
  padding: 2rem 2rem;
  width: 100%;
  flex: 1;
  min-width: 0;
}

article h1 { font-size: 2rem; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
article h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
article h3 { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.5rem; }
article h4 { font-size: 1rem; margin-top: 1.25rem; margin-bottom: 0.25rem; }

article p { margin: 0.75rem 0; }

article a { color: var(--accent); text-decoration: none; }
article a:hover { text-decoration: underline; }

article ul, article ol { margin: 0.75rem 0; padding-left: 2rem; }
article li { margin: 0.25rem 0; }

article blockquote {
  border-left: 4px solid var(--accent);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: var(--bg-alt);
  color: var(--fg-muted);
}

article code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.875em;
  background: var(--code-bg);
  padding: 0.2em 0.4em;
  border-radius: 4px;
}

article pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}

article pre code {
  background: none;
  padding: 0;
  font-size: 0.85em;
  line-height: 1.5;
}

article table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
  overflow-x: auto;
  display: block;
}

article th, article td {
  border: 1px solid var(--border);
  padding: 0.5rem 0.75rem;
  text-align: left;
}

article th { background: var(--bg-alt); font-weight: 600; }
article tr:nth-child(even) { background: var(--bg-alt); }

article img { max-width: 100%; height: auto; border-radius: 6px; }

article hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

footer {
  text-align: center;
  padding: 1.5rem;
  color: var(--fg-muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .sidebar-toggle { display: block; }
  .sidebar {
    position: fixed;
    left: -260px;
    top: 49px;
    height: calc(100vh - 49px);
    z-index: 99;
    transition: left 0.2s ease;
    border-right: 1px solid var(--border);
    box-shadow: none;
  }
  .sidebar-open .sidebar {
    left: 0;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }
  main { padding: 1rem; }
  article h1 { font-size: 1.5rem; }
  article pre { font-size: 0.8em; }
}
"""

HIGHLIGHT_CSS = """\
/* Code syntax highlighting - GitHub style */
.codehilite { background: var(--code-bg); border-radius: 6px; }
.codehilite .hll { background-color: #ffffcc }
.codehilite .c { color: var(--fg-muted); font-style: italic }
.codehilite .k { color: #cf222e; font-weight: bold }
.codehilite .o { color: var(--fg) }
.codehilite .cm { color: var(--fg-muted); font-style: italic }
.codehilite .cp { color: #cf222e }
.codehilite .c1 { color: var(--fg-muted); font-style: italic }
.codehilite .cs { color: var(--fg-muted); font-style: italic }
.codehilite .gd { color: #82071e; background-color: #ffebe9 }
.codehilite .gi { color: #116329; background-color: #dafbe1 }
.codehilite .gs { font-weight: bold }
.codehilite .gu { color: #6e7781 }
.codehilite .kc { color: #cf222e; font-weight: bold }
.codehilite .kd { color: #cf222e; font-weight: bold }
.codehilite .kn { color: #cf222e; font-weight: bold }
.codehilite .kp { color: #cf222e }
.codehilite .kr { color: #cf222e; font-weight: bold }
.codehilite .kt { color: #953800 }
.codehilite .m { color: #0550ae }
.codehilite .s { color: #0a3069 }
.codehilite .na { color: #116329 }
.codehilite .nb { color: #953800 }
.codehilite .nc { color: #953800; font-weight: bold }
.codehilite .no { color: #0550ae }
.codehilite .nd { color: #8250df }
.codehilite .ni { color: var(--fg) }
.codehilite .ne { color: #953800; font-weight: bold }
.codehilite .nf { color: #8250df }
.codehilite .nl { color: #0550ae }
.codehilite .nn { color: #953800 }
.codehilite .nt { color: #116329 }
.codehilite .nv { color: #0550ae }
.codehilite .ow { color: #cf222e; font-weight: bold }
.codehilite .w { color: var(--fg) }
.codehilite .mf { color: #0550ae }
.codehilite .mh { color: #0550ae }
.codehilite .mi { color: #0550ae }
.codehilite .mo { color: #0550ae }
.codehilite .sb { color: #0a3069 }
.codehilite .sc { color: #0a3069 }
.codehilite .sd { color: #0a3069 }
.codehilite .s2 { color: #0a3069 }
.codehilite .se { color: #0a3069 }
.codehilite .sh { color: #0a3069 }
.codehilite .si { color: #0a3069 }
.codehilite .sx { color: #0a3069 }
.codehilite .sr { color: #0a3069 }
.codehilite .s1 { color: #0a3069 }
.codehilite .ss { color: #0a3069 }
.codehilite .bp { color: #953800 }
.codehilite .vc { color: #0550ae }
.codehilite .vg { color: #0550ae }
.codehilite .vi { color: #0550ae }
.codehilite .il { color: #0550ae }
"""


def title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def collect_pages(content_dir: Path) -> list[dict]:
    pages = []
    for md_file in sorted(content_dir.rglob("*.md")):
        rel = md_file.relative_to(content_dir)
        html_rel = rel.with_suffix(".html")
        # Read first heading as title, fallback to filename
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

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    (SITE_DIR / "style.css").write_text(CSS, encoding="utf-8")
    (SITE_DIR / "highlight.css").write_text(HIGHLIGHT_CSS, encoding="utf-8")

    if not CONTENT_DIR.exists():
        CONTENT_DIR.mkdir(parents=True)
        # Create a sample index page
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

        # Calculate relative root path
        depth = len(page["html_rel"].parts) - 1
        root = "../" * depth if depth > 0 else ""

        sidebar = build_sidebar(pages, page["html_rel"], root)
        html = TEMPLATE.format(
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
