# Instagram → website gallery: nightly sync

Every night, GitHub copies the **8 newest posts** from @fatouafricanhairbraiding into the "Recent styles" gallery on the website. Post on Instagram as usual, and the website catches up by the next morning. No Instagram script runs on the website: the photos are stored with the site, so it stays fast.

Pieces in this repo:
- `scripts/instagram_sync.py` fetches the posts, crops each photo to 4:5, and rewrites the gallery between `<!-- IG-FEED:START -->` and `<!-- IG-FEED:END -->` in `public/index.html`. If anything fails, the site is left exactly as it was.
- `.github/workflows/instagram-sync.yml` runs the script every day at about 5 AM Chicago time, and on demand. It does nothing until `IG_TOKEN` is added.

## One-time setup (about 30 minutes, owner)

### 1. Make the Instagram account professional (free)
Instagram app → Profile → ☰ → **Settings and activity → Account type and tools → Switch to professional account** → choose **Business**, category "Hair salon".

### 2. Create a Meta developer app
1. Go to developers.facebook.com and log in with the Facebook account that manages the salon.
2. **My Apps → Create app.** When asked for the app type, choose **Business**. Name it e.g. "Fatou website gallery".
3. In the app, add the **Instagram** product.
4. Left menu: **Instagram → API setup with Instagram business login**.
5. Next to @fatouafricanhairbraiding, click **Generate token**, sign in to Instagram, and **copy the token**. It's valid for 60 days, and the sync renews it automatically (see step 4).

Meta's documentation says that if your app needs "Advanced Access", App Review is required. Reading your own account's posts normally doesn't need it. If the first run reports a permission error, tell me and I'll walk you through it.

### 3. Add the token to GitHub
github.com/lamine71/fatou-hair-braiding → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `IG_TOKEN`
- Value: the token from step 2

Never paste the token into chat, email, or the website code.

### 4. Optional, recommended: automatic token renewal
The sync renews the token every day. To let it save the renewed token by itself, so you never have to paste a new one:
1. github.com → your avatar → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Repository access: **only** `fatou-hair-braiding`. Permissions: **Secrets: Read and write**. Nothing else.
3. Add it to the repo as a secret named `SECRETS_PAT`, the same way as step 3.

Without `SECRETS_PAT`, paste a fresh `IG_TOKEN` (step 2.5 → step 3) about every 50 days.

### 5. Run it once
Repo → **Actions → Instagram sync → Run workflow**. After about a minute, check the gallery.

## Hosting note
The site is hosted free on **GitHub Pages** by `.github/workflows/pages.yml`, which publishes the `public/` folder. When the sync commits new photos, it starts that publish workflow itself, so the live site updates on its own a minute or two later.

If the site moves to Cloudflare Pages or Netlify later, those redeploy on every push, so the publish step can simply be removed.

## Notes
- Videos and Reels use their cover image. Multi-photo posts use the first photo. Posts Instagram flags for copyrighted music are skipped automatically.
- Hashtags and @mentions are stripped from the captions used for each photo's description.
- To show photos by hand instead, delete the workflow file and edit the gallery between the markers.
