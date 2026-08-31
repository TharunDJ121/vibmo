import urllib.request
import zipfile
import io
import os
import shutil

url = "https://github.com/Vincentwei1021/video-shotcraft/archive/refs/heads/main.zip"
print(f"Downloading from {url}...")

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = resp.read()
    print(f"Downloaded {len(data):,} bytes ({len(data)/(1024*1024):.2f} MB)")
    
    dest_final = os.path.join("third_party", "video-shotcraft")
    if os.path.exists(dest_final):
        shutil.rmtree(dest_final, ignore_errors=True)
        
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall("third_party")
        
    extracted = [n for n in os.listdir("third_party") if n.startswith("video-shotcraft-")][0]
    os.rename(os.path.join("third_party", extracted), dest_final)
    print(f"Extracted cleanly to {dest_final}!")
