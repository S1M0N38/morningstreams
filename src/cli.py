import argparse
import os

# Arguments parsing
parser = argparse.ArgumentParser(
    description="Expose acestreams from morningstreams in you local network.",
    epilog="Source code: https://github.com/S1M0N38/morningstreams",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--ip",
    default="127.0.0.1",
    help="ip where the m3u8 will be exposed",
)
parser.add_argument(
    "--port",
    default=8080,
    help="port where the m3u8 will be exposed",
)
parser.add_argument(
    "--username",
    default=os.getenv("MORNINGSTREAMS_USERNAME"),
    help="your morningstreams username",
)
parser.add_argument(
    "--password",
    default=os.getenv("MORNINGSTREAMS_PASSWORD"),
    help="your morningstreams password",
)
parser.add_argument(
    "--no-server",
    action="store_true",
    help="don't start http server to expose playlist.m3u8",
)
parser.add_argument(
    "--no-engine",
    action="store_true",
    help="don't start acestream engine in the background",
)
args = parser.parse_args()
