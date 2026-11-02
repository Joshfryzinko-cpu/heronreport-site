from PIL import Image
import io, hashlib
from pathlib import Path
img_dir = Path("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/img/stories")
src = img_dir / "59c40dfcfd0844df.jpg"
img = Image.open(src).convert("RGB")
print(f"Original: {img.size}", flush=True)
img.thumbnail((900, 600), Image.LANCZOS)
print(f"Resized: {img.size}", flush=True)
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
data = buf.getvalue()
new_md5 = hashlib.md5(data).hexdigest()[:16]
print(f"New md5: {new_md5}, size: {len(data)}", flush=True)
new_path = img_dir / f"{new_md5}.jpg"
new_path.write_bytes(data)
print(f"Saved: {new_path}", flush=True)
print(f"OLD_MD5=59c40dfcfd0844df")
print(f"NEW_MD5={new_md5}")
