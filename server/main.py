import sqlite3
import hashlib
import socket
import threading
import pickle
import rsa

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))

server.listen()

public_key, private_key = rsa.newkeys(1024)

clients = {}


def handle_connection(client, addr):
    while client:
        recv = client.recv(2048)
        try:
            pickled = pickle.loads(recv)
        except:
            pickled = [""]
        print(pickled)
        if pickled[0] == "ping":
            client.send("pong".encode())

        elif pickled[0] == "public key":

            clients[addr] = {}
            clients[addr]['public key'] = rsa.PublicKey.load_pkcs1(pickled[1])
            client.send(public_key.save_pkcs1("PEM"))
        else:
            try:
                recv = pickle.loads(rsa.decrypt(recv, private_key))
                request_packet = recv[0]
                if request_packet == "login":
                    username = recv[1][0]
                    password = hashlib.sha256(recv[1][1].encode()).hexdigest()

                    conn = sqlite3.connect("userdata.db")
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))
                    dat = cur.fetchall() and "1" or "0"
                    client.send(rsa.encrypt(
                        dat.encode(), clients[addr]['public key']))
            except Exception as e:
                print(e)
                client.send("BAD KEY".encode())


while True:
    client, addr = server.accept()
    threading.Thread(target=handle_connection, args=(
        client, str(addr[0])+str(addr[1]))).start()
