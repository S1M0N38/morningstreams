import http.server
import socketserver
import threading


class HTTPServer:
    def __init__(self, ip, port):
        self.handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((ip, port), self.handler)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )

    def start(self):
        print("Starting HTTP server...", end=" ", flush=True)
        self.server_thread.start()
        print("✓")

    def stop(self):
        print("Stoping HTTP server...", end=" ", flush=True)
        self.server.shutdown()
        print("✓")
