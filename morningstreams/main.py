import hashlib
import pathlib
import subprocess
import tarfile
import time
import urllib.request

from .core.cli import args
from .core.client import MorningstreamsClient
from .core.engine import AcestreamEngine
from .core.server import HTTPServer

repo = pathlib.Path(__file__).parent.parent
path_tar_gz = repo / "acestream.tar.gz"
path_acestream_engine = repo / "acestream.engine"
path_playlist = repo / "playlist.m3u8"


def install():

    # Download acestream-engine for Rasberry PI
    version = "acestream_3.1.48_Py2.7.16%2B_LinaroNDK_webUI_ARMv7.tar.gz"
    url = (
        "https://github.com/moromete/repository.moromete.addons/"
        "raw/master/plugin.video.streams/" + version
    )
    sha265 = "a4a73f84f33139ec5c0decdf1c1edc1a9d83737eac3ce6df2005e1099826e297"

    print("Removing old acestream engine if exists...", end=" ", flush=True)
    path_tar_gz.unlink(missing_ok=True)
    subprocess.run(
        ["sudo", "rm", "-rf", path_acestream_engine],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    if path_acestream_engine.exists():
        print("✗")
        msg = "You have to reboot the Raspberry Pi (sudo reboot) and try again"
        raise PermissionError(msg)
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
    tar.extractall(path=repo)
    tar.close()
    print("✓")

    print("Removing acestream.tar.gz...", end=" ", flush=True)
    path_tar_gz.unlink()
    print("✓")


def run():

    # Remove previous playlist
    path_playlist.unlink(missing_ok=True)

    # Create and start HTTP server
    server = HTTPServer(args.ip, args.port)
    if not args.no_server:
        server.start()

    # Create and start Acestream engine
    engine = AcestreamEngine(
        path_acestream_engine / "acestream.start",
        path_acestream_engine / "acestream.stop",
    )
    if not args.no_engine:
        engine.start()

    # Get streams and save into playlist.m3u8
    with MorningstreamsClient(args.username, args.password) as ms:
        with open(path_playlist, "w") as f:
            f.write(ms.generate_m3u8(args.ip))

    try:
        if not args.no_server:
            address = f"http://{args.ip}:{args.port}/playlist.m3u8"
            print(f"Exposing streams at {address}")

        # TODO instead of this time.sleep, perform diagnostic about
        # the running stream and reload if it's stuck
        time.sleep(60 * 60 * 4)

    except KeyboardInterrupt:
        print()
        if not args.no_server:
            server.stop()
        if not args.no_engine:
            engine.stop()
