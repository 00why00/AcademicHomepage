# Haoyu Wang — Academic Homepage

Source for [haoyuwang.com](https://haoyuwang.com/), built with Jekyll and GitHub Pages.
[中文维护说明](docs/README-zh.md)

## Edit the site

| File | Purpose |
| --- | --- |
| `_config.yml` | Site URL, description, profiles and analytics |
| `_includes/homepage/intro.md` | Biography and research interests |
| `_includes/homepage/news.md` | Dated research updates |
| `_includes/homepage/pub.md` | Selected publications and Scholar IDs |
| `_includes/homepage/others.md` | Education, experience and reviewing |
| `_data/navigation.yml` | Navigation labels and section anchors |
| `assets/js/main.js`, `citations.js` | Native browser interactions; no bundler or npm install required |
| `_sass/_homepage.scss`, `_sidebar.scss` | Site navigation, accessibility and profile styles |

Keep reusable content in `_includes/`. Only intended standalone pages belong in `_pages/`.
Use `relative_url` for local links and assets, and explicit heading IDs for navigation.
Earlier section hashes remain as compatibility anchors.

A citation span uses the full `citation_for_view` ID from the corresponding Google Scholar paper:

```html
<span class="paper-citations" data-scholar-id="PBNh1BIAAAAJ:IjCSPb-OGe4C"></span>
```

Missing records and unavailable citation data do not prevent the rest of the page from rendering.
The browser tries the raw data branch first and falls back to jsDelivr if that host is unavailable.
Set `google_scholar_stats_use_cdn` to reverse this preference.
The full publication list is linked on Google Scholar; only verified publication changes should be added here.

## Local preview and checks

Install Ruby **3.3.10** (see `.ruby-version`) with your preferred Ruby version manager.
The lockfile supports Apple Silicon macOS, Linux and Windows. Node **22+** is only needed for JavaScript tests; Python **3.12** is used by the crawler.

```sh
gem install bundler -v 2.6.9
bundle install
bash run_server.sh
```

Open [localhost:4000](http://127.0.0.1:4000). Google Analytics is loaded only in production builds.

Before publishing:

```sh
node --test tests/*.test.js
python3 -m unittest discover -s tests -p 'test_*.py'
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 scripts/check_site.py _site
```

The **Site checks** workflow runs these checks for pushes and pull requests.
It checks generated local links, section anchors, publication images, metadata, the manifest,
and accidental publication of internal files. Also check mobile navigation, keyboard focus and
the 924/925/926 px boundary after layout changes.

## Publication images

Retain full-resolution PNGs in `images/`. The homepage loads responsive WebP derivatives;
clicking a figure opens its original image. Figures below the fold use lazy loading.

To regenerate derivatives, use an isolated Python environment with Pillow **12.3.0**:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install Pillow==12.3.0
.venv/bin/python scripts/optimize_images.py
```

Add a new image name to `NAMES` in that script and use `paper-image.html` in the publication
entry. Commit the generated `images/publications/` files and `_data/paper_images.json`.
The image script only resizes and encodes supplied images; it does not generate scientific content.

## Citation updates

The **Get Citation Data** workflow runs daily at 08:00 UTC, after Pages builds, and on manual
dispatch. It reads the existing repository secret `GOOGLE_SCHOLAR_ID` and updates the existing
`google-scholar-stats` branch after a complete, validated fetch.

Attempts are bounded: one direct request attempt followed by up to two proxy attempts, each
limited to 120 seconds with 15 seconds between attempts. Exhaustion exits unsuccessfully
without replacing the last valid snapshot. Workflow runs are serialized, and publishing
preserves the data branch's history.

To run locally:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r google_scholar_crawler/requirements.txt
GOOGLE_SCHOLAR_ID=PBNh1BIAAAAJ .venv/bin/python google_scholar_crawler/main.py
```

Dependency changes belong in `google_scholar_crawler/requirements.in`. Regenerate the lock using
Python 3.12 and pip-tools 7.6.1, then test a clean installation and the import check:

```sh
.venv/bin/python -m pip install pip-tools==7.6.1
.venv/bin/python -m piptools compile --generate-hashes --upgrade google_scholar_crawler/requirements.in
.venv/bin/python -m pip install --require-hashes -r google_scholar_crawler/requirements.txt
.venv/bin/python -c 'from scholarly import scholarly; from bibtexparser.bibdatabase import BibDatabase'
```

The compatibility bounds on bibtexparser and httpx are intentional: scholarly uses the
bibtexparser 1.x module layout and the pre-0.28 httpx proxy argument.
A successful Pages deployment and a successful citation refresh are separate checks.

## Publishing

GitHub Pages publishes the repository's main branch using the domain in `CNAME`.
Keep build dependencies, tests, crawler scripts and internal fragments out of the public output.
After deployment, verify the homepage, sitemap, citation display and Actions results.

Codex-assisted commits follow the attribution instructions in [AGENTS.md](AGENTS.md).

## Credits

Based on [AcadHomepage](https://github.com/RayeRen/acad-homepage.github.io).
The original template incorporates Font Awesome under SIL OFL 1.1 and MIT licenses and is
influenced by [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) and
[Academic Pages](https://github.com/academicpages/academicpages.github.io), both under the MIT License.
