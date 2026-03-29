# CUBRID Code Analysis

A static site with in-depth code analysis and notes on the [CUBRID](https://github.com/CUBRID/cubrid) database engine internals.

## Project Structure

```
content/          # Markdown source files (one .md = one page)
templates/        # HTML template, CSS, and JS (source of truth for styling/layout)
site/             # Generated output (gitignored, rebuilt from scratch)
build.py          # Static site generator script
justfile          # Build/serve/watch commands
```

## Usage

Requires Python 3 with `markdown` and `pymdown-extensions` (auto-installed on first run).

```bash
# Build the site
just build

# Build and serve locally at http://localhost:8000
just serve

# Watch for changes and auto-rebuild (requires entr)
just watch
```

## Adding Content

1. Add a `.md` file to `content/`
2. Run `just build`
3. The page appears in the sidebar automatically, titled from the first `# heading`

## Customizing Appearance

Edit files in `templates/` directly:

- `base.html` — page layout and structure
- `style.css` — main stylesheet
- `highlight.css` — code syntax highlighting colors
- `theme.js` — dark/light theme toggle logic
