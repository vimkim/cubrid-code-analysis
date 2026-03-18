# CUBRID Code Analysis - Static Site

# Build the site
build:
    python3 build.py

# Serve locally on port 8000
serve: build
    python3 -m http.server -d site 8000

# Watch for changes and rebuild (requires entr)
watch:
    find content -name '*.md' | entr -r just serve

# Clean generated site
clean:
    rm -rf site
