import hashlib
import random
import socket
import threading
import encrypt_decrypt
import json
import time

class Server:
    def __init__(self, address, key=None, port=5050, ip="127.0.0.1", format="utf-8"):
        self.clients, self.names = [], []
        self.symbs = symbs
        self.port = port
        self.ip = ip
        self.address = address
        self.address = (ip, port)
        self.key = key
        self.key = self.generate_key(self.symbs)
        self.format = format

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        print(f"Server is working on {self.ip}:{self.port}")
        self.start_chat()

    def generate_key(self, symbs):
        key = ""
        for i in range(len(symbs)):
            key += encrypt_decrypt.do_magic(self.symbs[i], self.symbs[len(self.symbs)-1-i])
        return str(key)

    def client_accept(self, conn):
        print("Sending request...")
        try:
            dict_to_client = {
                "symbs": symbs,
                "phrase": "".join(random.choice(symbs) for i in range(64))
            }
            dict_to_client = json.dumps(dict_to_client, indent=2)
            conn.send(dict_to_client.encode(self.format))

            print("Receiving response...")
            dict_from_client = conn.recv(1024).decode(self.format)
            dict_from_client = json.loads(dict_from_client)
            name = dict_from_client["name"]
            handshake_phrase = dict_from_client["phrase"]

            print("Checking up handshake...")
            if handshake_phrase == hashlib.sha1(
                    (json.loads(dict_to_client)["phrase"] + "RACCOON.ME").encode(self.format)).hexdigest():
                self.clients.append(conn)
                self.names.append(name)
                self.broadcast_message(
                    encrypt_decrypt.do_magic(f"{name} has joined the chat!", self.key).encode(self.format))
                print("Key: " + self.key)
                thread = threading.Thread(target=self.handle, args=[conn, name])
                thread.start()
                print(f"{name} connected!")
                conn.send(encrypt_decrypt.do_magic("Connection successful!", self.key).encode(self.format))
                print(f"Total active connections {len(self.clients)}\n")
            else:
                raise ConnectionRefusedError
        except Exception as e:
            print(f"Connection killed! [{e}]")
            conn.close()

    def start_chat(self):
        self.server.listen()
        while len(self.clients) <= 20:
            conn, addr = self.server.accept()
            accept = threading.Thread(target=self.client_accept, args=[conn])
            accept.start()

    def handle(self, conn, name):
        while True:
            try:
                message = conn.recv(1024)
                send = threading.Thread(target=self.broadcast_message, args=[message])
                send.start()
            except:
                self.clients.pop(self.clients.index(conn))
                self.names.pop(self.names.index(name))
                conn.close()
                break

    def broadcast_message(self, message):
        for client in self.clients:
            client.send(message)


symbs = "ghijklmnopqrstuwvxyz"
symbs += symbs.upper()
symbs += "1234567890"
symbs += "!<>=+-/';?"

main = Server(symbs)
main.start_server()
