from sqlite3 import connect
from hashlib import sha256
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from pickle import dumps, loads
from rsa import newkeys, PublicKey, decrypt, encrypt, DecryptionError
from time import time
from string import ascii_letters
from random import choice

server = socket(AF_INET, SOCK_STREAM)
server.bind(("localhost", 9999))

server.listen()

public_key, private_key = newkeys(2048)

session_ids = {"": None}


def create_session_id(client):
    session_id = ""
    while session_id in session_ids:
        session_id = ''.join(choice(ascii_letters) for i in range(128))
    session_ids[client['addr']] = session_id
    client['session_id'] = session_id


clients = {}

logged_in = {}


def send(client, data):
    client['client'].send(encrypt(dumps(data), client['public key']))


def handle_connection(client, addr):
    while client:
        try:
            recv = client.recv(2048)
        except (ConnectionAbortedError, ConnectionResetError):
            print("Client discomnnected?")
        try:
            pickled = loads(recv)
        except:
            pickled = [""]
        if pickled[0] == "ping":
            client.send(str((time()) - pickled[1]).encode())
        elif pickled[0] == "public key":
            clients[addr] = {}
            clients[addr]['addr'] = addr
            clients[addr]['public key'] = PublicKey.load_pkcs1(pickled[1])
            clients[addr]['session_id'] = ""
            clients[addr]['client'] = client
            client.send(public_key.save_pkcs1("PEM"))
        else:
            try:
                recv = loads(decrypt(recv, private_key))
                request_packet = recv[0]
                if request_packet == "login":
                    username = recv[1][0]
                    security = recv[1][1]

                    conn = connect("userdata.db")
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT * FROM userdata WHERE username = ? AND password = ?", (username, sha256(security.encode()).hexdigest()))
                    username_fetch = cur.fetchall()
                    cur.execute(
                        "SELECT * FROM sessions WHERE username = ? AND session_id = ?", (username, security))
                    session_fetch = cur.fetchall()
                    if username_fetch or session_fetch:
                        if not session_fetch:
                            create_session_id(clients[addr])
                            cur.execute(
                                "DELETE * FROM sessions WHERE username = ? AND session_id = ?", (username, security))
                        send(clients[addr], {
                             'STATUS': 1, 'SESSION ID': clients[addr]['session_id']})
                        logged_in[username] = {}
                        logged_in[username]['session_id'] = clients[addr]['session_id']
                        cur.execute("INSERT INTO sessions (username, session_id) VALUES (?, ?)",
                                    (i[0], clients[addr]['session_id']))
                        conn.commit()
                    else:
                        send(clients[addr], {
                             'STATUS': 0, 'ERROR': 'Invalid username or password'})
                else:
                    if 'session_id' not in recv[2]:
                        send(clients[addr],
                             {'STATUS': 0, 'ERROR': 'INVALID SESSION ID'})
                    if clients[addr]['session_id'] != "" and recv[2]['session_id'] == clients[addr]['session_id']:
                        print("valid request")
            except DecryptionError:
                client.send("BAD KEY".encode())


def create_database():
    conn = connect("userdata.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL
        )
        """)


while True:
    create_database()
    client, addr = server.accept()
    Thread(target=handle_connection, args=(
        client, str(addr[0])+str(addr[1]))).start()
