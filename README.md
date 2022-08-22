# morningstreams

> This content is not affiliated with, endorsed, sponsored, or specifically
> approved by Morningstreams.

Sometimes I want to watch acestream on my **computer** and sometimes on my
**TV** (with LG WebOS) so I came up with the following solution which suited to
both circumstances. I expose a [m3u8](https://en.wikipedia.org/wiki/M3U)
playlist on my local network which streams point to a running acestream engine
using [acestream HTTP API](https://docs.acestream.net/en/developers/api-reference/#playback-endpoints).

I decided to automate the whole process of starting a
[morningstreams](https://morningstreams.com) stream in a single python CLI
program. It can be run on **macOS** and on **raspberry pi**.

## :arrow_down: Installation

```bash
pipx install morningstreams
```
[pipx](https://pypa.github.io/pipx/) is similar to pip but it is better suited
to install CLI python application like morningstreams. I suggest you to take a
look, otherwise you can still use your favorite package manager (e.g. pip).

## :zap: Usage

- You need a morningstreams account (https://discord.gg/fYj5qZW).
- A VPN is suggest but not necessary 
([install VPN on RPI](https://gist.github.com/S1M0N38/77ad8d3cb5e481aa802d43636881279c))

I develop and test this program on macOS (Intel processor with Big Sur) and on
Raspberry Pi (Raspberry Pi 3 Model B with Raspbian 11).

If you are on macOS [Docker](https://docs.docker.com/desktop/install/mac-install/)
must be run it the background while using this program.

To install the acestream engine use
```bash
moringstreams install
```
This operation is required to be run only the first time. You can run it again
if you want to reinstall acestream engine (on raspberry you likely need a reboot
and the run `moringstreams install` again). 

Authenticate with
```bash
moringstreams login
```
This command will ask to input your morningstreams credentials and store them
for the future. If you don't want to type the credentials you can provide them
using `MORNINGSTREAMS_USERNAME` and `MORNINGSTREAMS_PASSWORD` environment
variables (Even if you use env vars you must run `moringstreams login`).

Run the acestream engine in the background, get streams from morningstreams and
expose m3u8 playlist on your local network with
```bash
morningstreams run
```
<kbd>Ctrl+C</kbd> quit the program in a clean manner.

### Options

The Command Line Interface (CLI) is pretty minimal; when in doubt just use
`--help`. Here are some examples

```
$ morningstreams --help

Usage: morningstreams [OPTIONS] COMMAND [ARGS]...

  Expose acestreams from morningstreams in you local network.
  Source code: https://github.com/S1M0N38/morningstreams

Options:
  --help  Show this message and exit.

Commands:
  install  Install acestream engine
  login    Login and store credentials for furture logins
  logout   Delete login credentials if exists
  run      Expose streams on your local network
  status   Show login status
```

```
$ morningstreams run --help

Usage: morningstreams run [OPTIONS]

  Expose streams on your local network

Options:
  --ip TEXT               Ip where playlist is exposed.  [default: 127.0.0.1]
  --port INTEGER          Port where playlist is exposed.  [default: 8080]
  --server / --no-server  Expose playlist.m3u8.  [default: server]
  --engine / --no-engine  Start acestream engine.  [default: engine]
  --help                  Show this message and exit.
```

## :tv: Watch the streams

Suppose that the program is running and exposing the playlist at 
`http://192.168.178.101:8080/playlist.m3u8` (I was able to specify the ip using
the `--ip` option). Every device in you local network visiting this address will
see the playlist. I can watch streams with:

- a TV with LG WebOS thanks to F-Player
- a computer using a video player which support HTTP Live Stream protocol

On computer I use [mpv](https://mpv.io/) with some options
```bash
mpv --no-resume-playback --rebase-start-time=no\
    --cache=no --cache-pause-wait=3 --audio-buffer=0\
    --stream-buffer-size=4k --pause=no\
    http://192.168.178.101:8080/playlist.m3u8
```
Just use an alias in your .zshrc/.bashrc to avoid to type this all the time:
`alias f1="mpv --no-resume-play..."`.


## :wrench: How it works 

```
┏━━━━━━━━━━━━━━━━━━━━━morningstreams━━━━━━━━━━━━━━━━━━━━━┓
┃                                                        ┃
┃                                      GET acestream ids ┃
┃                   ┌─────────────┐──────────────────────╋─────▶┌────────────────────────┐
┃                   │   client    │                      ┃      │ api.morningstreams.com │
┃                   └─────────────┘◀─────────────────────╋──────└────────────────────────┘
┃                          │           acestream ids     ┃
┃                          │                             ┃
┃                  generate playlist                     ┃
┃                          │                             ┃GET playlist.m3u8
┃ server───────────────────┼────────────────────────┐◀───╋─────────────────┌──────────────┐
┃ │                        ▼                        │    ┃                 │ video player │
┃ │ ┏━playlist.m3u8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │────╋────────────────▶└──────────────┘
┃ │ ┃ #EXTM3U                                     ┃ │    ┃playlist.m3u8                   ▲
┃ │ ┃ #EXTINF:-1, Server 1                        ┃ │    ┃                        stream  │
┃ │ ┃ http://[--ip]:[--port]/ace/getstream?id=13f…┃ │    ┃                                │
┃ │ ┃ #EXTINF:-1, Server 2 (backup)               ┃ │    ┃ ┌────────────────────────┐     │
┃ │ ┃ http://[--ip]:[--port]/ace/getstream?id=3e8…┃ │    ┃ │    acestream engine    │     │
┃ │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │    ┃ │   (wrapped in docker   │     │
┃ └─────────────────────────────────────────────────┘    ┃ │container if necessary) │◀────┘
┃                                                        ┃ │                        │
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ └────────────────────────┘
```

TODO: explain the schematic
