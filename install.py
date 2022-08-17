import tarfile
import pathlib
import shutil
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

print("Removing old acestream engine...", end=" ", flush=True)
path_tar_gz.unlink(missing_ok=True)
shutil.rmtree(path_acestream_engine, ignore_errors=True)
print("✓")

print("Downloading acestream.tar.gz...", end=" ", flush=True)
with open(path_tar_gz, "wb") as f:
    with urllib.request.urlopen(url) as resp:
        f.write(resp.read())
print("✓")

print("Extracting to acestream.engine...", end=" ", flush=True)
tar = tarfile.open(path_tar_gz, "r:gz")
tar.extractall()
tar.close()
print("✓")

print("Removing acestream.tar.gz...", end=" ", flush=True)
path_tar_gz.unlink()
print("✓")
