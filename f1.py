#!/usr/bin/env python3
"""
Simple HTTP server for exposing .m3u8 playlist on your local network 
Usage::
    python3 f1.py

Original code for http server:
    https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
"""
import os
import http.server
import socketserver
import sys

import requests

PORT = 8080
ADDRESS = ('', PORT)
LOCAL_IP = sys.argv[1]

username = os.getenv('MORNINGSTREAMS_USERNAME')
password = os.getenv('MORNINGSTREAMS_PASSWORD')

# Check if username and password are set
if not username or not password:
    raise ValueError('''
        MORNINGSTREAMS_USERNAME and/or MORNINGSTREAMS_PASSWORD environment
        variables are not correctly set.'''
    )

# Check if ACE stream Engine is running
# try:
#     requests.get('http://127.0.0.1:6878/webui/api/service')
# except requests.exceptions.ConnectionError:
#     raise EnvironmentError('ACE stream engine is not running.')


# Login Morningstreams
login_url = 'https://api.morningstreams.com/api/users/login'
credentials = {'username': username, 'password': password, 'rememberMe': False}
response = requests.post(login_url, json=credentials)
assert response.json()['success']
token = response.json()['token']


# Update IP
update_id_url = 'https://api.morningstreams.com/api/posts/update_ip'
headers = {'authorization': token}
ace_ip = {'aceIP': requests.get('https://wtfismyip.com/text').text.strip()}
response = requests.post(update_id_url, headers=headers, json=ace_ip)
assert response.json()['aceIP'] == ace_ip['aceIP']


# ACE Stream
posts_url = 'https://api.morningstreams.com/api/posts'
response = requests.get(posts_url, headers=headers)
m3u8 = '#EXTM3U\n'
for link in response.json():
    try:
        int(link["text"], 16)  # check if is a acestream link
        m3u8 += f'#EXTINF:-1,{link["title"]}\n'
        m3u8 += f'http://{LOCAL_IP}:6878/ace/getstream?id={link["text"]}\n'
    except ValueError:
        pass

with open('playlist.m3u8', 'w') as f:
    f.write(m3u8)

httpd = socketserver.TCPServer(ADDRESS, http.server.SimpleHTTPRequestHandler)
print(f'Starting httpd... http://{LOCAL_IP}:{PORT}/playlist.m3u8')
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
print('\nStopping httpd...')
