import pickle
from customtkinter import *
from functools import partial
from connection import ConnectionHandler

class LoginApp():
    def __init__(self):
        self.CONNECTION_HANDLER = ConnectionHandler("localhost", 9999)
        self.connection_attempts = 1

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

        CTkLabel(master=self.frame, text="Login System",
                 text_font=("Roboto", 24)).pack(pady=12, padx=10)

        username_entry = CTkEntry(
            master=self.frame, placeholder_text="Username")
        username_entry.pack(pady=12, padx=10)

        password_entry = CTkEntry(
            master=self.frame, placeholder_text="Password", show="​")
        password_entry.pack(pady=12, padx=10)
        button = CTkButton(master=self.frame, text="Login", command=lambda: self.login(
            username_entry.get(), password_entry.get())).pack(pady=12, padx=10)

        self.checkbox = CTkCheckBox(master=self.frame, text="Remember Me")
        self.checkbox.pack(pady=12, padx=10)

        self.error_label = CTkLabel(master=self.frame, text="",
                                    text_color="red", text_font=("Roboto", 8))
        self.error_label.pack(pady=12, padx=10)

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
                 text_color="red", text_font=("Roboto", 24)).pack(pady=12, padx=10)
        CTkButton(master=self.frame, text="Reconnect",
                  command=self.reconnect).pack(pady=12, padx=10)

    def attempt_login(self, username, password):
        client = self.CONNECTION_HANDLER.get_client()
        if not self.CONNECTION_HANDLER.is_connected():
            self.connection_lost()
        self.CONNECTION_HANDLER.send("login", [username, password])
        recv = self.CONNECTION_HANDLER.recv(1024)
        return (recv and recv == "1")

    def login(self, username, password):
        print("yes", username, password)
        login_result = self.attempt_login(username, password)
        if not login_result:
            self.error_label.set_text("Invalid username or password")
        else:
            self.error_label.set_text("Login success")
