import pathlib
import platform

import click

from . import utils

repo = pathlib.Path(__file__).parent.parent
path_credentials = repo / "credentials.txt"


@click.group()
def cli():
    """
    \b
    Expose acestreams from morningstreams in you local network.
    Source code: https://github.com/S1M0N38/morningstreams
    """
    pass


@cli.command(help="Install acestream engine")
def install():
    """This script prints hello NAME COUNT times."""
    if utils.is_raspberrypi():
        utils.installer_rpi()
        click.secho("Acestream engine installed.", fg="green", bold=True)
    elif utils.is_macos():
        msg = "Is docker (https://docs.docker.com) running in the backgound?"
        if click.confirm(msg):
            utils.installer_macos()
            click.secho("Acestream engine installed.", fg="green", bold=True)
    else:
        msg = (
            f"{platform.system()} - {platform.machine()} is not supported. "
            "You can still run the script with --no-engine flag."
        )
        raise EnvironmentError(msg)


@cli.command(help="Login and store credentials for furture logins")
@click.option("--username", prompt=True, envvar="MORNINGSTREAMS_USERNAME")
@click.password_option(envvar="MORNINGSTREAMS_PASSWORD")
def login(username, password):
    if utils.valid_credentials(username, password):
        with open(path_credentials, "w") as f:
            f.write(f"{username}\n{password}")
        click.secho("Sucessfully logged in.", fg="green", bold=True)
    else:
        click.secho("Invalid credendial.", fg="red", bold=True)


@cli.command(help="Show login status")
def status():
    if path_credentials.exists():
        with open(path_credentials) as f:
            username = f.readline().strip()
        click.echo(f"Your are logged in as {username}.")
    else:
        click.echo("Your are not logged in.")


@cli.command(help="Delete login credentials if exists")
def logout():
    if path_credentials.exists():
        path_credentials.unlink()
        click.echo("Sucessfully logged out.")
    else:
        click.echo("Your are not logged in.")


@cli.command(help="Expose streams on your local network")
@click.option(
    "--ip",
    default="127.0.0.1",
    show_default=True,
    help="Ip where playlist is exposed.",
)
@click.option(
    "--port",
    type=int,
    default=8080,
    show_default=True,
    help="Port where playlist is exposed.",
)
@click.option(
    "--server/--no-server",
    default=True,
    show_default=True,
    help="Expose playlist.m3u8.",
)
@click.option(
    "--engine/--no-engine",
    default=True,
    show_default=True,
    help="Start acestream engine.",
)
def run(**args):
    if not path_credentials.exists():
        msg = "You have to be logged in. Use morningstream login"
        click.secho(msg, fg="yellow")
        return
    with open(path_credentials) as f:
        username = f.readline().strip()
        password = f.readline().strip()
    utils.run(username, password, args)


if __name__ == "__main__":
    cli()
