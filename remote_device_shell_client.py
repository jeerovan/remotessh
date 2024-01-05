import asyncio
import websockets
import json
import paramiko
import logging
import struct

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
try:
    from types import UnicodeType
except ImportError:
    UnicodeType = str

# Create a logger
logger = logging.getLogger(__name__)

# Set the log level
logger.setLevel(logging.INFO)

# Create a handler to write the logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(console_handler)

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.ssh_client = None
        self.ssh_shell = None
        self.timeout = 1

    async def connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(self.uri)
                await self.on_connect()
                await self.listen()
            except Exception as e:
                logger.error("Connection failed:%s",e)
                await asyncio.sleep(5)  # Adjust the delay as needed for reconnection.

    async def on_connect(self):
        """
        Implement actions to be performed when the WebSocket connection is established.
        """
        logger.info("Websocket Connected")

    async def on_message(self, message):
        """
        Implement actions to be performed when a message is received.
        """
        logger.info("Websocket Message:%s",message)
        try:
            msg = json.loads(message)
        except JSONDecodeError:
            return

        if not isinstance(msg, dict):
            return

        resize = msg.get('resize')
        if resize and len(resize) == 2:
            try:
                if self.ssh_shell:
                    self.ssh_shell.resize_pty(*resize)
            except (TypeError, struct.error, paramiko.SSHException):
                pass

        data = msg.get('data')
        if data and isinstance(data, UnicodeType):
            if self.ssh_shell:
              self.ssh_shell.send(data)
        if isinstance(message,str):
          data = json.loads(message)
          if data.get("task") == "shell_connect":
            if self.ssh_shell:
              await self.clear_ssh()
            username = data.get("user")
            password = data.get("pass")
            await self.open_ssh(username,password)

    async def open_ssh(self,username,password):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect('localhost', 22, username, password)
        except paramiko.SSHException:
            await self.send_message("CHANCLOSED".encode('utf-8'))
            return

        self.ssh_shell = self.ssh_client.invoke_shell(term='xterm-256color')
        self.ssh_shell.setblocking(0)

        # Start listening for SSH shell data in the background.
        asyncio.create_task(self.receive_ssh_data())
        logger.info("Shell Opened")

    async def receive_ssh_data(self):
        """
        Receives data from the SSH shell and sends it to the WebSocket.
        """
        while True:
            data = None
            try:
              if self.ssh_shell:
                data = self.ssh_shell.recv(1024)
            except (OSError,IOError) as e:
                await asyncio.sleep(.2)
                continue
            if not data:
                break
            await self.send_message(data)
            if self.ssh_shell.closed:
                await self.clear_ssh()
                await self.send_message("CHANCLOSED".encode('utf-8'))
                break

    async def on_close(self, reason):
        """
        Implement actions to be performed when the WebSocket connection is closed.
        """
        logger.info("Websocket Closed")
        await self.clear_ssh()
        await asyncio.sleep(5)  # Adjust the delay as needed for reconnection.

    async def clear_ssh(self):
        if self.ssh_shell:
            self.ssh_shell.close()
        if self.ssh_client:
            self.ssh_client.close()
        self.ssh_client = None
        self.ssh_shell = None
        logger.info("Shell Closed")

    async def listen(self):
        try:
            async for message in self.websocket:
                await self.on_message(message)
        except websockets.ConnectionClosed as e:
            await self.on_close(e.reason)
            self.websocket = None

    async def send_message(self, message):
        if self.websocket:
            await self.websocket.send(message)

if __name__ == "__main__":
    # default params (Should be setup if run as a service)
    host = None
    device_id = None
    email_id = None # optional if host is not abona.in

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-host","--host",help="host. example: abona.in")
    parser.add_argument("-did","--device_id",help="unique device id")
    parser.add_argument("-eid","--email_id",help="email id")
    args = parser.parse_args()

    host = args.host or host
    device_id = args.device_id or device_id
    email_id = args.email_id or email_id

    should_run = True

    if not device_id:
      logger.error("device id is required")
      should_run = False
    if not host:
      logger.error("host is required")
      should_run = False
    else:
      if "abona" in host.lower() and not email_id:
        logger.error("email is required")
        should_run = False
    
    if not should_run:
        exit()
    Uri = "wss://" + host + "/rsws?did=" + device_id
    if email_id:
      Uri = Uri + "&eid=" + email_id
    async def main():
        client = WebSocketClient(Uri)
        await client.connect()

    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()

