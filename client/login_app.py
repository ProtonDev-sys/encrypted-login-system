import pickle
from customtkinter import *
from functools import partial
from connection import ConnectionHandler


class LoginApp():
    def __init__(self):
        self.CONNECTION_HANDLER = ConnectionHandler("localhost", 9999)
        self.connection_attempts = 1
        self.session_id = None

    def run(self):
        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.root = CTk()
        self.root.geometry("500x350")
        self.root.title("Login")
        self.frame = CTkFrame(master=self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        if not self.CONNECTION_HANDLER.is_connected():
            self.connection_lost()
        else:
            self.build_widgets()
        self.root.mainloop()

    def build_widgets(self):

        CTkLabel(master=self.frame, text="Login System").pack(pady=12, padx=10)

        username_entry = CTkEntry(
            master=self.frame, placeholder_text="Username")
        username_entry.pack(pady=12, padx=10)

        self.password_entry = CTkEntry(
            master=self.frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12, padx=10)
        button = CTkButton(master=self.frame, text="Login", command=lambda: self.login(
            username_entry.get(), self.password_entry.get())).pack(pady=12, padx=10)

        self.checkbox = CTkCheckBox(
            master=self.frame, text="Remember Me", command=self.visible_password)
        self.checkbox.pack(pady=12, padx=10)

        self.error_label = CTkLabel(master=self.frame, text="",
                                    text_color="red")
        self.error_label.pack(pady=12, padx=10)

    def visible_password(self):
        if self.checkbox.get() == 1:
            character = ""
        else:
            character = "*"
        self.password_entry.configure(show=character)

    def reconnect(self):
        client = self.CONNECTION_HANDLER.get_client()
        self.connection_attempts += 1
        if self.CONNECTION_HANDLER.is_connected():
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.CONNECTION_HANDLER.connect()
            self.connection_attempts = 1
            self.build_widgets()
        else:
            self.connection_lost()

    def connection_lost(self):
        if not self.frame:
            return
        for widget in self.frame.winfo_children():
            widget.destroy()
        CTkLabel(master=self.frame, text=f"Connection failed!\nReconnect attempt {self.connection_attempts}",
                 text_color="red").pack(pady=12, padx=10)
        CTkButton(master=self.frame, text="Reconnect",
                  command=self.reconnect).pack(pady=12, padx=10)

    def attempt_login(self, username, password):
        client = self.CONNECTION_HANDLER.get_client()
        if not client:
            self.connection_lost()
        self.CONNECTION_HANDLER.send("login", [username, password])
        recv = self.CONNECTION_HANDLER.recv(2048)
        return recv

    def login(self, username, password):
        login_result = self.attempt_login(username, password)
        print(login_result)
        if login_result['STATUS'] == 0:
            self.error_label.configure(text=login_result['ERROR'])
        else:
            self.session_id = login_result['SESSION ID']
