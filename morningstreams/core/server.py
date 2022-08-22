import http.server
import os
import socketserver
import threading


class HTTPServer:
    def __init__(self, ip, port, directory):
        self.handler = http.server.SimpleHTTPRequestHandler
        self.directory = directory
        self.prev_directory = os.getcwd()
        self.server = socketserver.TCPServer((ip, port), self.handler)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )

    def start(self):
        print("Starting HTTP server...", end=" ", flush=True)
        os.chdir(self.directory)
        self.server_thread.start()
        print("✓")

    def stop(self):
        print("Stoping HTTP server...", end=" ", flush=True)
        self.server.shutdown()
        os.chdir(self.prev_directory)
        print("✓")
