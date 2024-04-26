import tkinter as tk
from tkinter import messagebox, ttk
from database import check_login, create_account

class LoginWindow:
    def __init__(self, parent, login_success_callback):
        self.parent = parent
        self.login_success_callback = login_success_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Login")
        
        tk.Label(self.window, text="Username:", font=("Arial", 12)).pack(pady=5, padx=10)
        self.username_entry = tk.Entry(self.window, font=("Arial", 12))
        self.username_entry.pack(pady=5, padx=10)

        tk.Label(self.window, text="Password:", font=("Arial", 12)).pack(pady=5, padx=10)
        self.password_entry = tk.Entry(self.window, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5, padx=10)

        ttk.Button(self.window, text="Login", command=self.login).pack(pady=5, padx=10)
        ttk.Button(self.window, text="Create Account", command=self.create_account_prompt).pack(pady=5, padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if check_login(username, password):
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            self.window.destroy()
            self.login_success_callback(username, password)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def create_account_prompt(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if create_account(username, password):
            messagebox.showinfo("Success", "Account created successfully. Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists or error creating account.")
