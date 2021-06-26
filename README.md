# morningstreams

Sometime I want to watch acestream on my **computer** and sometimes on my **TV**
(with LG WebOS) so I came up with the following setup which suited to both
circumstance.

### requirements
- [moringstreams](http://morningstreams.com/) account
- [Docker desktop](https://www.docker.com/) installed
- python3 installed
- computer with static LAN IP (mine is `192.168.178.100`) connect with Ethernet.

Morningstreams account credential are used to get acestream link.
Docker is the simplest way to run acestream Engine on Mac OS.
Python3 is used as scripting language to make requests to morningstreams API and
to spawn a simple server where serve acestream link to your local network.

### my setup
This is **my** setup so it won't be **your** ideal setup; nevertheless it could
inspire you on how to develop your own.

1. Acestream Engine running on my **computer** inside to 
   `magnetikonline/acestream-server` container. To run this I use the following
   alias:
   ```zsh
   alias ace="docker run --publish 6878:6878 --rm --tmpfs \
             '/dev/disk/by-id:noexec,rw,size=4k' \
             magnetikonline/acestream-server"
   ```

2. Then, from inside this repository, I run
   ```zsh
   python3 f1.py 192.168.178.100
   ```
   This script requests to morningstreams API acestreams link available and
   organize write them in `playlist.m3u8` file. Then a simple http is spawned so
   `playlist.m3u8` is share across your local network. You can now see this file
   with all your device (including your TV) connect to your local network by
   visiting `http://192.168.178.100:8080/playlist.m3u8` (of course this address
   depend of your computer local IP).

3. **Computer**: use a player with HSL support open 
   `http://192.168.178.100:8080/playlist.m3u8`

3. **TV (LG WebOS)**: use F-Player to open 
   `http://192.168.178.100:8080/playlist.m3u8`.
