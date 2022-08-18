import subprocess
import time
import urllib.error
import urllib.request


class AcestreamEngine:
    def __init__(self, start_script, stop_script, timeout=10):
        self.start_script = start_script
        self.stop_script = stop_script
        self.timeout = timeout

    def start(self):
        if self.is_running:
            msg = "Another instance of Acestream engine is already running"
            question = "Would you like to restart it? [No] "
            restart = input(f"{msg}\n{question}") or "No"
            if restart.upper() in ["Y", "YES"]:
                self.stop()
                self.start()
            return
        print("Starting Acestream engine...", end=" ", flush=True)
        start_time = time.time()
        subprocess.Popen(["sudo", self.start_script])
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
        process = subprocess.Popen(["sudo", self.stop_script])
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
