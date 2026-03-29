# CLAUDE.md

## Project Overview

Static site generator for CUBRID database engine code analysis articles. Converts Markdown files in `content/` to styled HTML pages in `site/`.

## Build

```bash
just build        # build site
just serve        # build + serve at localhost:8000
just watch        # auto-rebuild on content changes
```

Or directly: `python3 build.py`

## Architecture

- `content/*.md` — source articles (one file = one page)
- `templates/` — HTML template (`base.html`), CSS (`style.css`, `highlight.css`), JS (`theme.js`)
- `build.py` — reads templates, converts markdown, writes to `site/`
- `site/` — generated output, gitignored, never edit directly

## Key Conventions

- The HTML template uses Python `str.format()` placeholders: `{title}`, `{content}`, `{sidebar_links}`, `{root}`
- Page titles are extracted from the first `# heading` in each markdown file
- Sidebar is auto-generated from all pages in `content/`
- Dark/light theme is handled via CSS custom properties and `data-theme` attribute
