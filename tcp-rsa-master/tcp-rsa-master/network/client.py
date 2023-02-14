#!/usr/bin/python3

import threading
import selectors
import socket

from rsa import RSA
from collections import deque


class TCPClient:
    def __init__(self, host, port, use_rsa=False, is_cli=False):
        self._host = host
        self._port = port
        self.rsa = RSA()
        self.use_rsa = use_rsa
        self.is_cli = is_cli
        self.server_public_key = None
        self.message_queue = deque()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._read_selector = selectors.DefaultSelector()
        self.connection_attempt = True

    def _input_and_send_loop(self):
        while True:
            msg = input("Your message: ")
            if self.use_rsa:
                msg = self.rsa.encode(msg, out_n=self.server_public_key)
            self.other.send(msg.encode("utf8"))

    def send_key(self):
        # key = "key: " + str(self.rsa.n)
        key = str(self.rsa.n)
        self.other.send(key.encode("utf-8"))

    def run(self):
        self.other.connect((self._host, self._port))
        self.send_key()
        if self.is_cli:
            threading.Thread(target=self._input_and_send_loop).start()
        while True:
            if self.connection_attempt:
                print("Connect to the server...\n")
                msg = self.other.recv(1024).decode("utf8")
                self.server_public_key = int(msg)
                print(f"Server public key received and is {self.server_public_key}")
                self.connection_attempt = False
            else:
                msg = self.other.recv(1024).decode("utf8")
                if self.use_rsa:
                    msg = self.rsa.decode(msg)
                if self.is_cli:
                    print("Server:  " + msg)
                self.message_queue.append(msg)

    @property
    def other(self):
        return self._socket

    @property
    def endpoint_pubkey(self):
        return self.server_public_key


if __name__ == "__main__":
    client = TCPClient("localhost", 8790, use_rsa=True, is_cli=True)
    client.run()
