import hashlib
import pathlib
import shutil
import tarfile
import urllib.request

here = pathlib.Path(__file__).parent

# Download acestream-engine for Rasberry PI
path_tar_gz = here / "acestream.tar.gz"
path_acestream_engine = here / "acestream.engine"
version = "acestream_3.1.48_Py2.7.16%2B_LinaroNDK_webUI_ARMv7.tar.gz"
url = (
    "https://github.com/moromete/repository.moromete.addons/"
    "raw/master/plugin.video.streams/" + version
)
sha265 = "a4a73f84f33139ec5c0decdf1c1edc1a9d83737eac3ce6df2005e1099826e297"

print("Removing old acestream engine...", end=" ", flush=True)
path_tar_gz.unlink(missing_ok=True)
shutil.rmtree(path_acestream_engine, ignore_errors=True)
print("✓")

print("Downloading acestream.tar.gz...", end=" ", flush=True)
with open(path_tar_gz, "wb") as f:
    with urllib.request.urlopen(url) as resp:
        f.write(resp.read())
print("✓")

print("Checking SHA256 for acestream.tar.gz...", end=" ", flush=True)
hash = hashlib.sha256()
with open(path_tar_gz, "rb") as f:
    for block in iter(lambda: f.read(4096), b""):
        hash.update(block)
assert sha265 == hash.hexdigest()
print("✓")

print("Extracting to acestream.engine...", end=" ", flush=True)
tar = tarfile.open(path_tar_gz, "r:gz")
tar.extractall()
tar.close()
print("✓")

print("Removing acestream.tar.gz...", end=" ", flush=True)
path_tar_gz.unlink()
print("✓")
