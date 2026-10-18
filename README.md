# Fatou Hair Braiding: website

The website for **Fatou Hair Braiding**, an African hair-braiding salon at 7124 S Jeffery Blvd on Chicago's South Side.

- **Live preview:** https://lamine71.github.io/fatou-hair-braiding/
- Hosted free on GitHub Pages. Every change pushed to the `site` branch republishes it automatically.

## What's here
| Path | What it is |
|---|---|
| `public/` | The website itself (`index.html`, `privacy.html`, `robots.txt`, `assets/`). This is the only folder that's published. |
| `scripts/instagram_sync.py` | Pulls the newest Instagram posts into the "Recent styles" gallery |
| `.github/workflows/pages.yml` | Publishes `public/` to GitHub Pages |
| `.github/workflows/instagram-sync.yml` | Runs the Instagram sync every night (idle until set up) |
| `docs/instagram-sync.md` | One-time setup for the Instagram sync |

## Editing
Open `public/index.html` in a browser to preview; no server is needed. Search for `SETUP:` comments to find the things still to fill in. The main ones are:
- **Square booking link:** replace `https://SQUARE-BOOKING-LINK.invalid` on every Book button.
- **Photos:** the gallery fills itself once the Instagram sync is set up.
- **Ad tracking IDs:** the `CONFIG` block at the bottom of `index.html`. Nothing third-party loads while it's blank.

## Before launch
The site currently tells search engines **not to index it**, because it's a draft. At launch:
1. Remove the `noindex` meta tag in `public/index.html`.
2. Remove the `Disallow` line in `public/robots.txt`.
3. Point the custom domain at GitHub Pages.
