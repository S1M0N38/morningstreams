#!/usr/bin/env python3
import argparse
import http.server
import json
import os
import socketserver
from urllib import error, parse, request

import requests

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
login_url = "https://api.morningstreams.com/api/users/login"
login_url = "https://api.morningstreams.com/api/auth/login"
credentials = {
    "username": args.username,
    "password": args.password,
}
response = requests.post(login_url, json=credentials)
token = response.json()["token"]
headers = {"authorization": f"bearer {token}"}


# ACE Stream
acestream_url = "https://api.morningstreams.com/api/acestreams"
response = requests.get(acestream_url, headers=headers)


# Save links in m3u8 file
m3u8 = "#EXTM3U\n"
for link in response.json():
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
httpd = socketserver.TCPServer(address, http.server.SimpleHTTPRequestHandler)
print(f"Starting httpd... http://{args.ip}:{args.port}/playlist.m3u8")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
print("\nStopping httpd...")
