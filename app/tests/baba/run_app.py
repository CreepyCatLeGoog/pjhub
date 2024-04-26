import tkinter as tk
from login import LoginWindow
from main_app import MainApp
from database import initialize_db

def start_main_app(username, password):
    app = MainApp(root, username, password)

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    root.withdraw()  # Initially hide the main window

    def on_login_success(username, password):
        root.deiconify()  # Show the main window upon successful login
        start_main_app(username, password)

    login_window = LoginWindow(root, on_login_success)

    root.mainloop()
