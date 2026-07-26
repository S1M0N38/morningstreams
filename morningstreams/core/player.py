import shutil
import subprocess

import click

# Hardcoded mpv options per player. iina-cli accepts the same mpv options but
# requires the `--mpv-` prefix and rejects the `--no-` form, so boolean
# negations are expressed as `--mpv-<option>=no`.
PLAYER_OPTIONS = {
    "mpv": [
        "--no-resume-playback",
        "--rebase-start-time=no",
        "--cache=no",
        "--cache-pause-wait=3",
        "--audio-buffer=0",
        "--stream-buffer-size=4k",
        "--pause=no",
    ],
    "iina-cli": [
        "--mpv-resume-playback=no",
        "--mpv-rebase-start-time=no",
        "--mpv-cache=no",
        "--mpv-cache-pause-wait=3",
        "--mpv-audio-buffer=0",
        "--mpv-stream-buffer-size=4k",
        "--mpv-pause=no",
    ],
}


def launch(player, address):
    """Launch a media player pointing at the playlist (fire-and-forget).

    The player runs detached in its own session so it survives morningstreams
    and is closed by the user from the player GUI. A missing binary or a
    launch failure only emits a warning: exposing the stream always takes
    priority over the optional player.
    """
    if not shutil.which(player):
        msg = (
            f"{player} not found on PATH; skipping player. "
            f"Stream still exposed at {address}."
        )
        click.secho(msg, fg="yellow")
        return
    cmd = [player, *PLAYER_OPTIONS[player], address]
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as e:
        click.secho(f"Failed to launch {player}: {e}", fg="yellow")
