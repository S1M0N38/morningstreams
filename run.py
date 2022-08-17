import pathlib
import time

from src.cli import args
from src.client import MorningstreamsClient
from src.engine import AcestreamEngine
from src.server import HTTPServer


def main():

    here = pathlib.Path(__file__).parent

    # Remove previous playlist
    (here / "playlist.m3u8").unlink(missing_ok=True)

    # Create and start HTTP server
    server = HTTPServer(args.ip, args.port)
    if not args.no_server:
        server.start()

    # Create and start Acestream engine
    engine = AcestreamEngine(
        here / "acestream.engine" / "acestream.start",
        here / "acestream.engine" / "acestream.stop",
    )
    if not args.no_engine:
        engine.start()

    # Get streams and save into playlist.m3u8
    with MorningstreamsClient(args.username, args.password) as ms:
        with open(here / "playlist.m3u8", "w") as f:
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


if __name__ == "__main__":
    main()
