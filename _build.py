"""Extract latin/latin-ext woff2 URLs from Google Fonts CSS, download, rewrite CSS."""
import re
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent
src_css = (FONTS_DIR / "_source.css").read_text()

# Split on comments — each block is preceded by /* charset */
blocks = re.split(r"/\*\s*([\w-]+)\s*\*/", src_css)
# blocks = ['', 'cyrillic-ext', '@font-face{...}', 'cyrillic', '@font-face{...}', ...]

want = {"latin", "latin-ext"}
out_css_parts = []
download_queue = []

for i in range(1, len(blocks), 2):
    charset = blocks[i].strip()
    body = blocks[i + 1]
    if charset not in want:
        continue

    # Find font-family, weight, style
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    url = re.search(r"url\(([^)]+)\)", body).group(1)

    # Local filename
    fname = f"{fam.lower()}-{weight}{'-italic' if style == 'italic' else ''}-{charset}.woff2"
    local_path = FONTS_DIR / fname
    download_queue.append((url, local_path))

    # Rewrite block with local URL
    new_body = body.replace(url, f"./fonts/{fname}")
    out_css_parts.append(f"/* {charset} */{new_body}")

# Download
for url, path in download_queue:
    if path.exists():
        print(f"skip (exists): {path.name}")
        continue
    print(f"downloading: {path.name}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        path.write_bytes(r.read())

# Write combined CSS
combined = "\n".join(out_css_parts)
(FONTS_DIR.parent / "fonts.css").write_text(combined)
print(f"\nwrote fonts.css ({len(combined)} bytes), {len(download_queue)} font files")
