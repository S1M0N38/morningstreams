import subprocess
import time
import urllib.error
import urllib.request

import click


class AcestreamEngine:
    def __init__(self, start_cmd, stop_cmd, timeout=10):
        self.start_cmd = start_cmd
        self.stop_cmd = stop_cmd
        self.timeout = timeout

    def start(self):
        if self.is_running:
            click.echo("Another instance of Acestream engine is running.")
            if click.confirm("Would you like to restart it?"):
                self.stop()
                self.start()
            return
        print("Starting Acestream engine...", end=" ", flush=True)
        start_time = time.time()
        subprocess.Popen(self.start_cmd, stdout=subprocess.DEVNULL)
        while time.time() - start_time < self.timeout:
            if self.is_running:
                print("✓")
                return
            time.sleep(1)
        print("✗")
        raise EnvironmentError("Cannot start acestream engine.")

    def stop(self):
        print("Stoping Acestream engine...", end=" ", flush=True)
        if not self.is_running:
            print("✓")
            return
        start_time = time.time()
        process = subprocess.Popen(self.stop_cmd, stdout=subprocess.DEVNULL)
        process.wait()
        while time.time() - start_time < self.timeout:
            if not self.is_running:
                print("✓")
                return
            time.sleep(1)
        print("✗")
        raise EnvironmentError("Cannot stop acestream engine.")

    @property
    def is_running(self):
        url = "http://127.0.0.1:6878/webui/api/service?method=get_version"
        try:
            urllib.request.urlopen(url)
            return True
        except (urllib.error.URLError, ConnectionResetError):
            return False
