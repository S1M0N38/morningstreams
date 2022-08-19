import hashlib
import http.client
import io
import pathlib
import platform
import subprocess
import tarfile
import time
import urllib.request

import click

from .core.client import MorningstreamsClient
from .core.engine import AcestreamEngine
from .core.server import HTTPServer

# paths #######################################################################

repo = pathlib.Path(__file__).parent.parent
path_playlist = repo / "playlist.m3u8"


# platforms ###################################################################


def is_raspberrypi():
    try:
        with io.open("/sys/firmware/devicetree/base/model", "r") as m:
            if "raspberry pi" in m.read().lower():
                return True
    except Exception:
        pass
    return False


def is_macos():
    # TODO maybe check for architecture: intel vs arm
    if platform.system() == "Darwin":
        return True
    return False


# install #####################################################################


def installer_rpi():

    # Download acestream-engine for Rasberry PI
    version = "acestream_3.1.48_Py2.7.16%2B_LinaroNDK_webUI_ARMv7.tar.gz"
    url = (
        "https://github.com/moromete/repository.moromete.addons/"
        "raw/master/plugin.video.streams/" + version
    )
    sha265 = "a4a73f84f33139ec5c0decdf1c1edc1a9d83737eac3ce6df2005e1099826e297"
    path_tar_gz = repo / "acestream.tar.gz"
    path_acestream_engine = repo / "acestream.engine"

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

    with open(path_tar_gz, "wb") as f:
        with urllib.request.urlopen(url) as resp:
            length = int(resp.getheader("content-length"))
            with click.progressbar(
                length=length,
                label="Downloading acestream.tar.gz...",
                bar_template="%(label)s %(info)s",
            ) as bar:
                for _ in range(101):
                    chunk = resp.read(length // 100)
                    f.write(chunk)
                    bar.update(len(chunk))

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


def installer_macos():

    # Download and install acestream-engine for MacOs
    image = "magnetikonline/acestream-server"
    print("Removing old acestream engine if exists...")
    subprocess.run(["docker", "image", "rm", image])
    print("Install acestream engine...")
    subprocess.run(["docker", "pull", image])


# login #######################################################################


def valid_credentials(username, password):
    try:
        with MorningstreamsClient(username, password):
            return True
    except http.client.HTTPException:
        return False


# run #########################################################################


def _engine_commands():

    if is_raspberrypi():
        path_acestream_engine = repo / "acestream.engine"
        return (
            ["sudo", path_acestream_engine / "acestream.start"],
            ["sudo", path_acestream_engine / "acestream.stop"],
        )

    elif is_macos():
        return (
            [
                "docker",
                "run",
                "--name",
                "acestream",
                "--publish",
                "6878:6878",
                "--rm",
                "--tmpfs",
                "/dev/disk/by-id:noexec,rw,size=4k",
                "magnetikonline/acestream-server",
            ],
            ["docker", "container", "kill", "acestream"],
        )
    else:
        msg = (
            f"{platform.system()} - {platform.machine()} is not supported to "
            "run acestream engine. You can still run the script with "
            "--no-engine flag."
        )
        raise EnvironmentError(msg)


def run(username, password, args):

    # Remove previous playlist
    path_playlist.unlink(missing_ok=True)

    # Create and start HTTP server
    if args["server"]:
        server = HTTPServer(args["ip"], args["port"])
        server.start()

    # Create and start Acestream engine
    if args["engine"]:
        start_engine_cmd, stop_engine_cmd = _engine_commands()
        engine = AcestreamEngine(start_engine_cmd, stop_engine_cmd)
        engine.start()

    # Get streams and save into playlist.m3u8
    with MorningstreamsClient(username, password) as ms:
        with open(path_playlist, "w") as f:
            f.write(ms.generate_m3u8(args["ip"]))

    try:
        if args["server"]:
            address = f"http://{args['ip']}:{args['port']}/playlist.m3u8"
            click.secho(f"Exposing streams at {address}", fg="blue", bold=True)

        # TODO instead of this time.sleep, perform diagnostic about
        # the running stream and reload if it's stuck
        time.sleep(60 * 60 * 4)

    except KeyboardInterrupt:
        print()
        if args["server"]:
            server.stop()
        if args["engine"]:
            engine.stop()
