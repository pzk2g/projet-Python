#!/usr/bin/python3

import threading
import tkinter as tk
from tkinter import *
from network import TCPClient, TCPServer


class PopUp(tk.Toplevel):
    def __init__(self, *args):
        assert (
            len(args) > 0
        ), "You should add at least one argument for the popup to show"
        super().__init__()

        i = 0
        self.wm_title("Informations")
        self.bind("<Return>", self.save_args)
        self.entries = list()

        self.arg_dict = {arg: None for arg in args}
        self.entries = {arg: None for arg in args}

        for val in args:
            tk.Label(self, text=val).grid(row=i)
            self.entries[val] = tk.Entry(self)
            self.entries[val].grid(row=i, column=1)
            i += 1
        Button(self, text="Send", command=self.save_args).grid(row=i, column=0)
        Button(self, text="Close", command=lambda: self.destroy()).grid(row=i, column=1)

    def save_args(self, event=None):

        for key, entry in self.entries.items():
            self.arg_dict[key] = entry.get()

        self.destroy()


class ChatGui(tk.Tk):
    socket = None

    def __init__(self, is_server=True, use_rsa=False, default=True):
        super().__init__()
        self.send_zone = None
        self.text_zone = None
        if not default:
            self.withdraw()
            popup = PopUp("Host", "Port")
            self.wait_window(popup)
            self.args = popup.arg_dict
            assert "Host" in self.args.keys()
            assert "Port" in self.args.keys()
            self.args["Port"] = int(self.args["Port"])
            self.deiconify()
        else:
            self.args = {"Host": "localhost", "Port": 8790}

        self.is_server = is_server
        self.use_rsa = use_rsa
        self.create_socket()

        self.load_gui()
        self.after(100, self.update_text_area)
        threading.Thread(target=self.socket.run).start()

    def load_gui(self):
        self.title = "Chat Window by Dark Vador"
        FONT = "Helvetica 14"
        FONT_BOLD = "Helvetica 13 bold"
        txt = Text(self, font=FONT, width=60)
        txt.grid(row=1, column=0, columnspan=2)

        scrollbar = Scrollbar(txt)
        self.text_zone = txt
        scrollbar.place(relheight=1, relx=0.974)
        e = Entry(self, font=FONT, width=55)
        e.grid(row=2, column=0)
        self.send_zone = e
        Button(self, text="Send", font=FONT_BOLD, command=self.listen_send_button).grid(
            row=2, column=1
        )
        self.bind("<Return>", self.listen_send_button)

    def create_socket(self):
        if self.is_server:
            self.socket = TCPServer(
                self.args["Host"], self.args["Port"], self.use_rsa, is_cli=False
            )
        else:
            self.socket = TCPClient(
                self.args["Host"], self.args["Port"], self.use_rsa, is_cli=False
            )

    def listen_send_button(self, event=None):
        message = self.send_zone.get()
        chat_area_text = "You -> " + message
        self.text_zone.insert(END, "\n" + chat_area_text)
        self.send_zone.delete(0, END)

        self.send_message(message)

    def send_message(self, message):
        if self.use_rsa:
            message = self.socket.rsa.encode(message, out_n=self.socket.endpoint_pubkey)
        self.socket.other.send(message.encode("utf-8"))

    def update_text_area(self):
        while len(self.socket.message_queue) > 0:
            message = self.socket.message_queue.popleft()
            chat_area_text = "Other -> " + message
            self.text_zone.insert(END, "\n" + chat_area_text)
        self.after(100, self.update_text_area)


if __name__ == "__main__":
    app = ChatGui(is_server=False)
    app.mainloop()
