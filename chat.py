import tkinter.messagebox
import socket
import threading
from tkinter import *
import encrypt_decrypt
from is_json import *
import json
import hashlib
import sys
import random

# 5.101.50.196

PORT = 5050
SERVER = "192.168.0.104"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
is_key_received = False
is_my_message = False

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDRESS)
except:
    error = Tk()
    error.withdraw()
    tkinter.messagebox.showerror(title="Server error!", message="Server doesn't working now! Please, try again later.")
    sys.exit()


class Chat:
    def __init__(self):
        self.key = ""
        self.Window = Tk()
        self.Window.title("Login")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=255, height=100, background="#1d3557")
        self.pls = Label(self.Window, text="Please login to continue", background="#1d3557", foreground="#ec9a9a",
                         font="Consolas 14 bold")
        self.pls.place(x=5)
        self.line = Label(self.Window, width=450, bg="#e63946")
        self.line.place(width=500, y=25, height=3)
        self.labelName = Label(self.Window, text="Name: ", background="#1d3557", foreground="#a8dadc",
                               font="Consolas 12 bold")
        self.labelName.place(x=5, y=32)
        self.entryName = Entry(self.Window, background="#1d3557", foreground="#a8dadc", font="Consolas 14")
        self.entryName.place(width=150, height=20, x=100, y=35)
        self.entryName.focus()
        self.logIn = Button(self.Window, background="#457b9d", foreground="#a8dadc", text="Log In", font="Consolas 12 bold",
                         command=lambda: self.go_ahead(self.entryName.get()))
        self.logIn.place(width=245, height=30, x=5, y=60)
        self.Window.iconbitmap("raccoon.ico")
        self.Window.mainloop()

    def go_ahead(self, name):
        self.logIn.destroy()
        if not name or name.count(" ") == len(name):
            name = f"user_{random.randint(100000, 999999)}"
        while name.startswith(" "):
            name = " ".join(name.split())
        self.layout(name)
        rcv = threading.Thread(target=self.receive)
        rcv.start()

    def layout(self, name):
        self.name = name
        self.Window.title("Room")
        self.Window.resizable(width=True, height=True)
        self.Window.minsize(360, 480)
        self.Window.maxsize(480, 640)
        self.Window.configure(width=360, height=480, bg="#1d3557")
        self.labelHead = Label(self.Window, bg="#1d3557", fg="#a8dadc", text="RACCOON.ME", font="Consolas 14 bold")
        self.labelHead.place(rely=0.01, relwidth=1)
        self.line = Label(self.Window, bg="#ABB2B9", fg="#a8dadc")
        self.line.place(relwidth=1, y=35, height=3)
        self.textCons = Text(self.Window, bg="#1d3557", fg="#a8dadc", font="Consolas 14")
        self.textCons.place(relheight=0.83, relwidth=1, y=38)
        self.entryMsg = Entry(bg="#a8dadc", fg="#1d3557", font="Consolas 13")
        self.entryMsg.place(relwidth=0.75, relheight=0.07, rely=0.912, relx=0.01)
        self.entryMsg.focus()
        self.buttonMsg = Button(text="Send", font="Consolas 12 bold", background="#457b9d", foreground="#a8dadc",
                                command=lambda: self.send_button(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.78, rely=0.912, relheight=0.07, relwidth=0.21)
        self.textCons.config(cursor="arrow")
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, width=15, relx=0.96)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

    def send_button(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.send_message)
        snd.start()

    def receive(self):
        while True:
            global is_key_received, is_my_message
            message = client.recv(1024).decode(FORMAT)
            if is_json(message):
                dict_from_server = json.loads(message)
                handshake_phrase = dict_from_server["phrase"]
                handshake_phrase = hashlib.sha1((handshake_phrase + "RACCOON.ME").encode(FORMAT)).hexdigest()
                dict_to_server = {
                    "name": self.name,
                    "phrase": handshake_phrase
                }
                dict_to_server = json.dumps(dict_to_server, indent=2)
                client.send(dict_to_server.encode(FORMAT))
                symbs = dict_from_server["symbs"]
                is_key_received = True
                for i in range(len(symbs)):
                    self.key += encrypt_decrypt.do_magic(symbs[i], symbs[len(symbs)-1-i])
            else:
                message = encrypt_decrypt.do_magic(message, self.key)
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message + "\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                
    def send_message(self):
        global is_my_message
        while self.msg.startswith(" "):
            self.msg = ' '.join(self.msg.split())
        if len(self.msg) > 0:
            self.textCons.config(state=DISABLED)
            message = encrypt_decrypt.do_magic(f"{self.name}: {self.msg}", self.key)
            client.send(message.encode(FORMAT))

gui = Chat()
