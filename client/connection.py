import socket
import pickle
import rsa
from time import time


class ConnectionHandler():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.public_key, self.private_key = rsa.newkeys(1024)
        self.server_key = None
        self.last_request = []
        self.connect()

    def connect(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.ip, self.port))
            if not self.server_key:
                self.exchange_keys()
        except (ConnectionResetError, ConnectionRefusedError):
            pass

    def exchange_keys(self):
        self.client.send(pickle.dumps(
            ["public key", self.public_key.save_pkcs1("PEM")]))
        self.server_key = rsa.PublicKey.load_pkcs1(
            self.client.recv(1024))

    def ping(self):
        self.client.send(pickle.dumps(
            ["ping", time()]))
        return self.client.recv(1024).decode()

    def is_connected(self):
        try:
            print(self.ping())
            return True
        except:
            return False

    def get_client(self):
        if not self.is_connected():
            self.connect()
        return self.client

    def send(self, key, data):
        self.client.send(rsa.encrypt(pickle.dumps(
            [key, data]), self.server_key))
        self.last_request = [key, data]

    def recv(self, buffer):
        recv = self.client.recv(buffer)
        try:
            if recv.decode() == "BAD KEY":
                self.exchange_keys()
                self.send(self.last_request[0], self.last_request[1])
                recv = self.get_client().recv(buffer)
        except:
            ret = rsa.decrypt(recv, self.private_key).decode()
            return ret
