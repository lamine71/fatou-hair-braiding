"""Pull the latest Instagram posts into the website's "Recent styles" gallery.

Runs nightly in GitHub Actions (.github/workflows/instagram-sync.yml). It:
  1. reads the newest posts of @fatouafricanhairbraiding via the Instagram API (Instagram Login),
  2. saves up to 8 images into public/assets/instagram/ (resized to 4:5 WebP if Pillow is installed),
  3. rewrites the gallery between <!-- IG-FEED:START --> and <!-- IG-FEED:END --> in public/index.html.
If anything fails, the site is left exactly as it was.

Environment:
  IG_TOKEN    long-lived Instagram user access token (GitHub secret)
Options:
  --site-dir DIR    site folder (default: public)
  --count N         number of posts (default: 8)
  --fixture FILE    use a local JSON list of posts instead of the API (for testing)
  --refresh         also refresh the token and print the new one to $GITHUB_OUTPUT as new_token
"""
import argparse
import html
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request

API = "https://graph.instagram.com/v25.0"
REFRESH_URL = "https://graph.instagram.com/refresh_access_token"
START, END = "<!-- IG-FEED:START -->", "<!-- IG-FEED:END -->"
FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_type,media_url,thumbnail_url}"
TILE_W, TILE_H = 640, 800  # 4:5, matches the gallery tiles


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def fetch_posts(token, count):
    me = get_json(f"{API}/me?" + urllib.parse.urlencode({"fields": "user_id,username", "access_token": token}))
    user_id = me["user_id"]
    print(f"Account: @{me.get('username')}")
    url = f"{API}/{user_id}/media?" + urllib.parse.urlencode(
        {"fields": FIELDS, "limit": str(max(count * 3, 25)), "access_token": token})
    return get_json(url).get("data", [])


def image_url(post):
    kind = post.get("media_type")
    if kind == "VIDEO":
        return post.get("thumbnail_url")
    if kind == "CAROUSEL_ALBUM":
        for child in post.get("children", {}).get("data", []):
            u = child.get("thumbnail_url") if child.get("media_type") == "VIDEO" else child.get("media_url")
            if u:
                return u
    return post.get("media_url")  # omitted by Instagram for copyright-flagged media


def clean_caption(text):
    text = re.sub(r"#\w+", "", text or "")
    text = re.sub(r"@\w+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def save_image(src, dest_stem):
    """Download (or copy, for fixtures) an image; resize/crop to 4:5 WebP when Pillow is available."""
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src, timeout=60) as resp:
            data = resp.read()
    else:
        data = pathlib.Path(src).read_bytes()
    try:
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(data)).convert("RGB")
        w, h = img.size
        target = TILE_W / TILE_H
        if w / h > target:  # too wide: crop the sides
            nw = int(h * target)
            img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:  # too tall: crop top and bottom, keeping a little more of the top
            nh = int(w / target)
            top = max(0, int((h - nh) * 0.4))
            img = img.crop((0, top, w, top + nh))
        img = img.resize((TILE_W, TILE_H), Image.LANCZOS)
        out = dest_stem.with_suffix(".webp")
        img.save(out, "WEBP", quality=80, method=6)
    except ImportError:
        out = dest_stem.with_suffix(".jpg")
        out.write_bytes(data)
    return out


def build_html(items):
    lines = [START]
    for it in items:
        alt = it["alt"] or "Braided style by Fatou Hair Braiding"
        lines.append(
            f'        <figure><a class="shot ig" href="{html.escape(it["permalink"])}" rel="noopener" '
            f'aria-label="Open this post on Instagram">'
            f'<img src="assets/instagram/{it["file"]}" alt="{html.escape(alt)}" '
            f'loading="lazy" width="{TILE_W}" height="{TILE_H}"></a>'
            f'<figcaption>{html.escape(it["label"])}</figcaption></figure>')
    lines.append("        " + END)
    return "\n".join(lines)


def refresh_token(token):
    """Extend the token another 60 days. A failure here never fails the sync."""
    try:
        data = get_json(REFRESH_URL + "?" + urllib.parse.urlencode(
            {"grant_type": "ig_refresh_token", "access_token": token}))
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::Token refresh skipped ({exc}). Tokens must be at least 24 hours old to refresh.")
        return
    new = data.get("access_token", "")
    days = int(data.get("expires_in", 0)) // 86400
    print(f"Token refreshed; valid for about {days} more days.")
    runner_tmp = os.environ.get("RUNNER_TEMP")
    if runner_tmp and new:
        print(f"::add-mask::{new}")
        pathlib.Path(runner_tmp, "ig_new_token").write_text(new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", default="public")
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--fixture")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    site = pathlib.Path(args.site_dir)
    index = site / "index.html"
    page = index.read_text(encoding="utf-8")
    if START not in page or END not in page:
        sys.exit("Gallery markers not found in index.html; nothing changed.")

    token = os.environ.get("IG_TOKEN", "")
    if args.fixture:
        posts = json.loads(pathlib.Path(args.fixture).read_text())
    elif not token:
        sys.exit("IG_TOKEN is not set; nothing changed.")
    else:
        posts = fetch_posts(token, args.count)

    picked = [p for p in posts if image_url(p) and p.get("permalink")][: args.count]
    if not picked:
        sys.exit("No usable posts returned; nothing changed.")

    # Build everything in a staging folder first. The live site is touched only after every
    # image has downloaded, so a failure part-way through leaves the site exactly as it was.
    out_dir = site / "assets" / "instagram"
    stage = pathlib.Path(tempfile.mkdtemp(prefix="ig-stage-"))
    try:
        items = []
        for i, post in enumerate(picked, 1):
            f = save_image(image_url(post), stage / f"ig-{i}")
            cap = clean_caption(post.get("caption"))
            label = cap[:26].rstrip() + ("…" if len(cap) > 26 else "") if cap else "On Instagram"
            items.append({"file": f.name, "permalink": post["permalink"], "alt": cap[:140],
                          "label": label, "timestamp": post.get("timestamp")})
        (stage / "feed.json").write_text(json.dumps(items, indent=1))
        new_page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: build_html(items), page, flags=re.S)
    except Exception as exc:  # noqa: BLE001 - any failure must leave the site untouched
        shutil.rmtree(stage, ignore_errors=True)
        sys.exit(f"Sync failed ({exc}); nothing changed.")

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("ig-*"):
        old.unlink()
    for f in stage.iterdir():
        shutil.move(str(f), out_dir / f.name)
    shutil.rmtree(stage, ignore_errors=True)
    index.write_text(new_page, encoding="utf-8")
    print(f"Gallery updated with {len(items)} posts.")

    if args.refresh and token and not args.fixture:
        refresh_token(token)


if __name__ == "__main__":
    main()
