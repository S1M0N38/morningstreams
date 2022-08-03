# morningstreams

Sometimes I want to watch acestream on my **computer** and sometimes on my **TV**
(with LG WebOS) so I came up with the following solution which suited to both
circumstances.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━f1.py━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                               ┃
┃                                        GET acestream ids      ┃
┃                       ┌─────────────┐─────────────────────────╋────────▶┌────────────────────────┐
┃                       │   client    │                         ┃         │ api.morningstreams.com │
┃                       └─────────────┘◀────────────────────────╋─────────└────────────────────────┘
┃                              │         acestream ids          ┃
┃                              │                                ┃
┃                      generate playlist                        ┃
┃                              │                                ┃ GET playlist.m3u8
┃ server───────────────────────┼─────────────────────────────┐◀─╋───────────────────┌──────────────┐
┃ │                            ▼                             │  ┃                   │ video player │
┃ │ ┏━playlist.m3u8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │──╋──────────────────▶└──────────────┘
┃ │ ┃ #EXTM3U                                             ┃  │  ┃  playlist.m3u8                   ▲
┃ │ ┃ #EXTINF:-1, Server 1                                ┃  │  ┃                           stream │
┃ │ ┃ http://[--ip]:[--port]/ace/getstream?id=11fbb885a...┃  │  ┃                                  │
┃ │ ┃ #EXTINF:-1, Server 2 (backup)                       ┃  │  ┃ ┌──────────────────────────────┐ │
┃ │ ┃ http://[--ip]:[--port]/ace/getstream?id=32aeedc98...┃  │  ┃ │       acestream engine       │ │
┃ │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │  ┃ │ (wrapped in docker container │ │
┃ └──────────────────────────────────────────────────────────┘  ┃ │        if necessary)         │◀┘
┃                                                               ┃ │                              │
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ └──────────────────────────────┘
```


### Requirements

- [moringstreams](http://morningstreams.com/) account
- [Docker desktop](https://www.docker.com/) installed
- python3 installed
- computer with static LAN IP (mine is `192.168.178.100`) connect with Ethernet.

Morningstreams account credentials are used to get acestream links.
Credendials can be set as enviroment variables, e.g. in your `.bashrc`
```bash
export MORNINGSTREAMS_USERNAME="my_username"
export MORNINGSTREAMS_PASSWORD="my_password"
```
or passed as arguments while running the script:
```zsh
python3 f1.py --username "my_username" --password "my_password"
```
Docker is the simplest way to run acestream Engine on Mac OS.
Python3 is used as scripting language to make requests to morningstreams API and
to spawn a simple server where to serve acestream links to your local network.

### My setup
This is **my** setup so it won't be **your** ideal setup; nevertheless it could
inspire you on how to develop your own.

1. Acestream Engine is running on my **computer** inside to 
   `magnetikonline/acestream-server` container. To run this I use the following
   alias:
   ```zsh
   alias ace="docker run --publish 6878:6878 --rm --tmpfs \
             '/dev/disk/by-id:noexec,rw,size=4k' \
             magnetikonline/acestream-server"
   ```

2. Then, from inside this repository, I run
   ```zsh
   python3 f1.py --ip 192.168.178.100
   ```
   This script requests to morningstreams API acestreams link available and
   organize write them in `playlist.m3u8` file. Then a simple http is spawned so
   `playlist.m3u8` is shared across your local network. You can now see this file
   with all your devices (including your TV) connect to your local network by
   visiting `http://192.168.178.100:8080/playlist.m3u8` (of course this address
   depends on your computer local IP).


### Watch streams

- **Computer**: use a player with HSL support to open 
  `http://192.168.178.100:8080/playlist.m3u8`.

- **TV (LG WebOS)**: use F-Player to open 
  `http://192.168.178.100:8080/playlist.m3u8`.

-----
>*pro-tip*: to see all the arguemnts of `f1.py` script run
```bash
python3 f1.py --help
```

>*pro-tip*: if you just watch the stream on the same computer which is running
>the acestream engine and [mpv](https://mpv.io) is installed, simply use
```bash
python3 f1.py --mpv
```
