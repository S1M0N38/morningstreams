import http.client
import json


class MorningstreamsClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = None
        self.token = None

    def __enter__(self):
        self.client = http.client.HTTPSConnection("api.morningstreams.com")
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def login(self):
        print(f"Logging in as {self.username}...", end=" ", flush=True)
        path = "/api/auth/login"
        credentials = {"username": self.username, "password": self.password}
        headers = {"Content-type": "application/json"}
        self.client.request("POST", path, json.dumps(credentials), headers)
        response = json.loads(self.client.getresponse().read().decode("utf-8"))
        if "token" in response:
            self.token = response["token"]
            print("✓")
        else:
            print("✗")
            raise http.client.HTTPException(response)

    def get_streams(self):
        print("Getting acestreams...", end=" ", flush=True)
        assert self.token is not None
        path = "/api/acestreams"
        headers = {"authorization": f"bearer {self.token}"}
        self.client.request("GET", path, headers=headers)
        streams = json.loads(self.client.getresponse().read().decode("utf-8"))
        print(f"found {len(streams)}")
        for stream in streams:
            print(f"  - {stream['title']} 👍 {stream['likesCount']}")
        return streams

    def generate_m3u8(self, ip):
        s = "#EXTM3U\n"
        for link in self.get_streams():
            try:
                int(link["contentId"], 16)  # check if is a acestream link
                s += f'#EXTINF:-1,{link["title"]}\n'
                s += f'http://{ip}:6878/ace/getstream?id={link["contentId"]}\n'
            except ValueError:
                pass
        return s
