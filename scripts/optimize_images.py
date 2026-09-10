"""Generate responsive WebP derivatives; retain full-resolution PNG originals."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("JoDiffusion", "SRA", "PFD", "lbGen", "AdaptAnything", "GEL")


def main():
    metadata = {}
    output = ROOT / "images" / "publications"
    output.mkdir(exist_ok=True)
    for name in NAMES:
        with Image.open(ROOT / "images" / f"{name}.png") as original:
            metadata[name] = {}
            for width in (500, 1000):
                image = original.copy()
                image.thumbnail((width, 10000), Image.Resampling.LANCZOS)
                image.save(output / f"{name}-{width}.webp", "WEBP", quality=88, method=6)
                if width == 1000:
                    metadata[name] = {"width": image.width, "height": image.height}
    with Image.open(ROOT / "images" / "android-chrome-512x512.png") as image:
        image.thumbnail((350, 350), Image.Resampling.LANCZOS)
        image.save(ROOT / "images" / "avatar.webp", "WEBP", quality=90, method=6)
    # JSON is valid YAML and is also directly readable by Jekyll.
    (ROOT / "_data" / "paper_images.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {len(NAMES)} responsive paper images and an avatar.")


if __name__ == "__main__":
    main()
