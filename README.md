# Fatou Hair Braiding: website and launch kit

One-page website plus the setup packs for Square, Google Ads, Facebook/Instagram ads, and the Google/social profiles.

| Folder | What's in it | Goes online? |
|---|---|---|
| `public/` | The website (`index.html`, `privacy.html`, `robots.txt`, `assets/`) | **Yes**, this folder only |
| `setup/` | Internal setup packs and scripts | No |

## Setup packs
- `setup/square-setup.md`: services, deposits, braiders, reminders, policies, the "no braider names" test
- `setup/google-ads/campaign-settings.md` and `setup/google-ads/ads.md`: campaign settings and paste-in ads
  - `keywords-*.txt` and `negative-keywords.txt` paste straight into Google Ads.
  - Re-generate with `python3 setup/google-ads/make_files.py`; it also checks Google's character limits.
- `setup/meta-ads.md`: Facebook/Instagram campaign, instant replies, video shot list
- `setup/profiles.md`: Google Business Profile description and Instagram/Facebook/TikTok bios (all within the length limits)
- `setup/check_licenses.py`: checks the braiders' Illinois licenses. Names go in `setup/braiders.txt`, which git ignores.

## Placeholders to fill in before launch
Search the site for `SQUARE-BOOKING-LINK`, `$___`, `_ h`, `YOUR-DOMAIN` and `class="ph"` (yellow-highlighted text).

| Placeholder | Where | Replace with |
|---|---|---|
| `https://SQUARE-BOOKING-LINK.invalid` | `public/index.html` (every Book button), `setup/google-ads/make_files.py` | The Square booking-site link |
| `$___` and `_ h` | Price cards in `public/index.html` | Real starting prices and times, then remove the `ph` class |
| Hair included / payment / kids' ages / parking | `public/index.html` (yellow text) | Real answers |
| Gallery "Photo coming soon" | `public/index.html` | 6–10 photos (WebP, under ~150 KB each, only clients who said yes) |
| Facebook / TikTok links | Commented out in `public/index.html` | Real profile links |
| `CONFIG` IDs | Bottom of `public/index.html` | Google Ads conversion ID and labels, and the Meta Pixel ID |
| Canonical URL, og:image | `<head>` of `public/index.html` | The real domain and a share image |
| Logo and favicon | `public/assets/` | From the brand kit |

## Facts already filled in (verified)
- Address 7124 S Jeffery Blvd, Chicago, IL 60649 · phone (773) 363-5834 · map coordinates 41.76509, -87.57667
- Hours: every day 8 AM–8 PM (owner-provided)
- Illinois salon registration **#189022344**, active, expires **Nov 30, 2026** (data.illinois.gov)
- Google profile and review links (Place ID `ChIJ4x3ue1coDogRs-D86BgjIDI`)
- Instagram @fatouafricanhairbraiding

## Preview locally
Open `public/index.html` in a browser. No server is needed.

## Publishing (later)
The plan is a **private** GitHub repo with free static hosting of the `public/` folder only (e.g. Cloudflare Pages or Netlify), plus the custom domain. Nothing is published until the owner approves.
