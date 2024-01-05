import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpserver
import logging
import asyncio
import os
import json

# Create a logger
logger = logging.getLogger(__name__)

# Set the log level
logger.setLevel(logging.INFO)

# Create a handler to write the logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(console_handler)

# Sets to store WebSocket connections
remote_ws_devices = {}
local_ws_devices = {}

class RemoteWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        # get the device id
        device_id = self.get_argument("did")
        self.device_id = device_id
        # Add the new connection to the remote_ws_devices
        remote_ws_devices[device_id] = self
        logger.info("Connected %s",device_id)

    def on_message(self, message):
        # Send the message to local WebSocket connections
        local_ws = local_ws_devices.get(self.device_id)
        if local_ws:
          local_ws.write_message(message,binary=True)

    def on_close(self):
        # Remove the connection from the remote_ws_devices
        if self.device_id in remote_ws_devices:
          del remote_ws_devices[self.device_id]

class LocalWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        device_id = self.get_argument("did")
        username = self.get_argument("user")
        password = self.get_argument("pass")
        self.device_id = device_id
        # Add the new connection to the local_ws_devices
        local_ws_devices[device_id] = self
        # Send the message to connect to ssh
        remote_ws = remote_ws_devices.get(self.device_id)
        if remote_ws:
          message = json.dumps({"user":username,"pass":password,"task":"shell_connect"})
          remote_ws.write_message(message)

    def on_message(self, message):
        # Send the message to remote WebSocket connections
        remote_ws = remote_ws_devices.get(self.device_id)
        if remote_ws:
          remote_ws.write_message(message)

    def on_close(self):
        # Remove the connection from the local_ws_devices
        if self.device_id in local_ws_devices:
          del local_ws_devices[self.device_id]

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        # Serve the index.html file
        key = self.get_argument("key")
        devices = []
        # list devices only if key matches
        if key == "longkeywithspecialchars":
          devices = remote_ws_devices.keys()
        self.render("home.html",devices = devices)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                    (r"/rsws", RemoteWebSocketHandler),
                    (r"/lsws", LocalWebSocketHandler),
                    (r"/", HomeHandler)
                    ]
        settings = dict(
            cookie_secret="A6r4k4d46r4",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            debug=True
        )
        super().__init__(handlers, **settings)

async def main():
    app = Application()
    app.listen(2010)
    event = asyncio.Event()
    await event.wait()

if __name__ == "__main__":
    asyncio.run(main())
