#!/usr/bin/python3

import selectors
import socket
import threading

from rsa import RSA
from collections import deque


class TCPServer:
    def __init__(self, host, port, use_rsa=False, is_cli=True):
        """Initialise the server attributes."""
        self._host = host
        self._port = port
        self.client = None
        self.is_cli = is_cli
        self.use_rsa = use_rsa
        self.rsa = RSA()
        self.client_public_key = None
        self.message_queue = deque()
        self.connection_attempt = True
        self._socket = None
        self._read_selector = selectors.DefaultSelector()
        self._write_selector = selectors.DefaultSelector()

    def _accept_connection(self, sock):
        """Callback function for when the server is ready to accept a connection."""
        client, _ = sock.accept()
        print("Registering client...")
        self._read_selector.register(
            client, selectors.EVENT_READ, self._receive_message
        )
        self._write_selector.register(client, selectors.EVENT_WRITE)
        self.client = client
        if self.is_cli:
            threading.Thread(target=self._input_and_send_loop, args=[client]).start()

    def _input_and_send_loop(self, client):
        while True:
            msg = input("Your message: ")
            if self.use_rsa:
                msg = self.rsa.encode(msg, out_n=self.client_public_key)
            client.send(msg.encode("utf8"))

    def _receive_message(self, sock):
        """Callback function for when a client socket is ready to receive."""
        msg = sock.recv(1024)
        msg = msg.decode("utf-8")
        if self.connection_attempt:
            self.client_public_key = int(msg)
            print(f"Client public key received and is {self.client_public_key}")
            self.connection_attempt = False
            for key, _ in self._write_selector.select(
                0
            ):  # We use a selector here to handle events
                if key.fileobj is not sock:
                    continue
                rsa_public_key = str(self.rsa.n).encode("utf-8")
                key.fileobj.send(rsa_public_key)
        else:
            if self.use_rsa:
                msg = self.rsa.decode(msg)
            if self.is_cli:
                print("Client: ", msg)
            self.message_queue.append(msg)

    def _init_server(self):
        """Initialises the server socket."""

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._host, self._port))
        self._socket.listen()
        # Put the socket in the selector "bag":
        self._read_selector.register(
            self._socket,
            selectors.EVENT_READ,
            self._accept_connection,
        )

    def run(self):
        """Starts the server and accepts connections indefinitely."""

        self._init_server()
        print("Running server...\n")
        while True:
            for key, _ in self._read_selector.select():
                sock, callback = key.fileobj, key.data
                callback(sock)

    @property
    def other(self):
        return self.client

    @property
    def endpoint_pubkey(self):
        return self.client_public_key


if __name__ == "__main__":
    cs = TCPServer("localhost", 8790, use_rsa=True, is_cli=True)
    cs.run()
