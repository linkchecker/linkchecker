# Copyright (C) 2012 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Define http test support classes for LinkChecker tests.
"""
import time
import threading
import telnetlib
import miniboa
from . import LinkCheckTest


TIMEOUT = 5


class TelnetServerTest(LinkCheckTest):
    """Start/stop a Telnet server that can be used for testing."""

    def __init__(self, methodName="runTest"):
        """Init test class and store default ftp server port."""
        super().__init__(methodName=methodName)
        self.host = "localhost"
        self.port = None
        self.stop_event = threading.Event()
        self.server_thread = None

    def get_url(self, user=None, password=None):
        if user is not None:
            if password is not None:
                netloc = f"{user}:{password}@{self.host}"
            else:
                netloc = f"{user}@{self.host}"
        else:
            netloc = self.host
        return "telnet://%s:%d" % (netloc, self.port)

    def setUp(self):
        """Start a new Telnet server in a new thread."""
        super().setUp()
        self.port, self.server_thread = start_server(self.host, 0, self.stop_event)
        self.assertFalse(self.port is None)

    def tearDown(self):
        """Send QUIT request to telnet server."""
        self.stop_event.set()
        if self.server_thread is not None:
            self.server_thread.join(10)
            assert not self.server_thread.is_alive()


def start_server(host, port, stop_event):
    # Instantiate Telnet server class and listen to host:port
    clients = []

    def on_connect(client):
        clients.append(client)
        client.send("Telnet test server\nlogin: ")

    server = miniboa.TelnetServer(port=port, address=host, on_connect=on_connect)
    port = server.server_socket.getsockname()[1]
    t = threading.Thread(None, serve_forever, args=(server, clients, stop_event))
    t.start()
    # wait for server to start up
    tries = 0
    while tries < 5:
        tries += 1
        try:
            client = telnetlib.Telnet(timeout=TIMEOUT)
            client.open(host, port)
            client.write(b"exit\n")
            break
        except Exception:
            time.sleep(0.5)
    return port, t


def serve_forever(server, clients, stop_event):
    """Run poll loop for server."""
    while True:
        if stop_event.is_set():
            return
        server.poll()
        for client in clients:
            if client.active and client.cmd_ready:
                handle_cmd(client)


def handle_cmd(client):
    """Handle telnet clients."""
    msg = client.get_command().lower()
    if msg == "exit":
        client.active = False
    else:
        client.send("Password: ")
