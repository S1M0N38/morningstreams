#!/usr/bin/env python3
import argparse
import json
import os
import socketserver
from http import client, server
from urllib import error, request

# Arguments parsing
parser = argparse.ArgumentParser(
    description="Expose acestreams from morningstreams in you local network.",
    epilog="Source code: https://github.com/S1M0N38/morningstreams",
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
    "--mpv",
    action="store_true",
    help="open streams with mpv",
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
args = parser.parse_args()

# Check if username and password are set
if not args.username or not args.password:
    raise ValueError(
        """
        morningstreams credentials are not provided.
        Used the flags --username and --password or
        export MORNINGSTREAMS_USERNAME and MORNINGSTREAMS_PASSWORD
        environment variables."""
    )

# Check if ACE stream Engine is running
try:
    request.urlopen(f"http://{args.ip}:6878/webui/api/service")
except error.URLError:
    raise EnvironmentError("ACE stream engine is not running.")

# Login Morningstreams
conn = client.HTTPSConnection("api.morningstreams.com")
credentials = {
    "username": args.username,
    "password": args.password,
}

headers = {"Content-type": "application/json"}
conn.request("POST", "/api/auth/login", json.dumps(credentials), headers)
response = conn.getresponse()
token = json.loads(response.read().decode("utf-8"))["token"]
headers = {"authorization": f"bearer {token}"}
print(f"\nLogged in as {args.username} ✓")

# ACE Stream
conn.request("GET", "/api/acestreams", headers=headers)
response = conn.getresponse()
streams = json.loads(response.read().decode("utf-8"))
print(f"\nFound {len(streams)} streams:")
for stream in streams:
    print(f"  - {stream['title']} 👍 {stream['likesCount']}")
conn.close()

# Save links in m3u8 file
m3u8 = "#EXTM3U\n"
for link in streams:
    try:
        int(link["contentId"], 16)  # check if is a acestream link
        m3u8 += f'#EXTINF:-1,{link["title"]}\n'
        m3u8 += f'http://{args.ip}:6878/ace/getstream?id={link["contentId"]}\n'
    except ValueError:
        pass
with open("playlist.m3u8", "w") as f:
    f.write(m3u8)

# Spawn http server
address = ("", args.port)
url = f"http://{args.ip}:{args.port}/playlist.m3u8"
httpd = socketserver.TCPServer(address, server.SimpleHTTPRequestHandler)
print(f"\nStarting httpd at {url}")
print("Press Ctrl+C to stop the server.")
try:
    if args.mpv:
        options = """\
            --no-resume-playback\
            --rebase-start-time=no\
            --cache=no\
            --cache-pause-wait=3\
            --audio-buffer=0\
            --stream-buffer-size=4k\
            --pause=no\
            """
        print("Opening streams with mpv ...")
        os.system(f"mpv {options} playlist.m3u8")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
print("\nStopping httpd...")
