"""Validate the built site without making external network requests."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import urljoin, urlsplit, unquote
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.images = []
        self.meta = {}
        self.heads = 0
        self.h1s = 0
        self.citation_ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "head":
            self.heads += 1
        if tag == "h1":
            self.h1s += 1
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        if tag in ("a", "link") and attrs.get("href"):
            self.references.append(attrs["href"])
        if tag in ("script", "img") and attrs.get("src"):
            self.references.append(attrs["src"])
        if tag == "img":
            self.images.append(attrs)
            self.references.extend(part.strip().split()[0] for part in attrs.get("srcset", "").split(",") if part.strip())
        if "data-scholar-id" in attrs:
            self.citation_ids.append(attrs["data-scholar-id"])
        if tag == "button":
            assert attrs.get("aria-label"), "Unnamed button"


def local_file(root, url):
    path = root / unquote(urlsplit(url).path).lstrip("/")
    return path / "index.html" if not path.suffix else path


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    page = Page()
    page.feed((root / "index.html").read_text())
    assert page.heads == 1 and page.h1s == 1, "Expected one head and one main heading"
    for key in ["description", "og:description", "og:image", "twitter:card"]:
        assert page.meta.get(key), f"Missing metadata: {key}"
    assert len(page.citation_ids) == len(set(page.citation_ids)) == 6
    site_url = "https://haoyuwang.com/"
    for reference in page.references:
        url = urlsplit(urljoin(site_url, reference))
        if url.scheme not in ("http", "https") or url.netloc != urlsplit(site_url).netloc:
            continue
        assert local_file(root, url.geturl()).is_file(), f"Missing local target: {reference}"
        if url.fragment and url.path == "/":
            assert unquote(url.fragment) in page.ids, f"Missing anchor: {reference}"
    for image in page.images:
        assert image.get("alt") and image.get("width") and image.get("height"), image
        if "/publications/" in image["src"]:
            assert image.get("loading") == "lazy" and image.get("srcset")
    manifest = json.loads((root / "images/site.webmanifest").read_text())
    assert manifest["name"] and manifest["short_name"]
    for icon in manifest["icons"]:
        assert local_file(root, urljoin(site_url + "images/site.webmanifest", icon["src"])).is_file()
    sitemap = ET.parse(root / "sitemap.xml")
    for location in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        assert "/includes/" not in location.text, location.text
        assert local_file(root, location.text).is_file(), location.text
    for private_path in ["_pages/includes", "scripts", "tests", "google_scholar_crawler", "AGENTS.md", "README.md"]:
        assert not (root / private_path).exists(), f"Unexpected published path: {private_path}"
    print(f"Site checks passed: {len(page.images)} images, {len(page.references)} references, 6 citation IDs.")


if __name__ == "__main__":
    main()
