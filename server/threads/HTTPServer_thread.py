import threading
from serverviews import server_app

class HTTPServer(threading.Thread):
    """HTTP Server to handle browser and client conections and TEDS management.
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        server_app.run(host='0.0.0.0')