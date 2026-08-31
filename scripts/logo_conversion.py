from PIL import Image
import os
from pathlib import Path
import base64

src = "logo.png"
img = Image.open(src).convert("RGBA")

# Resize to 300 px wide while preserving aspect ratio.
target_w = 600
target_h = round(img.height * target_w / img.width)
resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

out = "logo.webp"

# Try lossless first, then progressively stronger compression if needed.
resized.save(out, "WEBP", lossless=True, method=6)
if os.path.getsize(out) > 200 * 1024:
    for quality in [95, 90, 85, 80, 75]:
        resized.save(out, "WEBP", quality=quality, method=6)
        if os.path.getsize(out) < 200 * 1024:
            break

size_kb = os.path.getsize(out) / 1024
print(f"Original: {img.size[0]}×{img.size[1]}")
print(f"Output: {resized.size[0]}×{resized.size[1]}")
print(f"File size: {size_kb:.1f} KB")


Path("logo.txt").write_bytes(base64.b64encode(Path("logo.webp").read_bytes()))
