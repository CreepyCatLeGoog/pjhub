import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import bcrypt
import os

DATABASE_NAME = "todo_app.db"

def initialize_db():
    """Create or open a database and create tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (username TEXT PRIMARY KEY, password_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, username TEXT, task TEXT, priority INTEGER, finished INTEGER,
                  FOREIGN KEY(username) REFERENCES accounts(username))''')
    conn.commit()
    conn.close()

class TodoAppGUI:
    def __init__(self, root):
        self.root = root
        
        initialize_db()  # Ensure the database and tables are initialized

        # Initialize task_listbox
        self.task_listbox = None

        # Create a login window
        self.create_login_window()

    def create_account_window(self):
        """Create a new window for account creation."""
        account_window = tk.Toplevel(self.root)
        account_window.title("Create Account")

        tk.Label(account_window, text="Username:", font=("Arial", 12)).pack(pady=(10, 2), padx=50, fill='both', expand=True)
        username_entry = tk.Entry(account_window, font=("Arial", 12))
        username_entry.pack(pady=(0, 10), padx=50, fill='both', expand=True)

        tk.Label(account_window, text="Password:", font=("Arial", 12)).pack(pady=(10, 2), padx=50, fill='both', expand=True)
        password_entry = tk.Entry(account_window, show="*", font=("Arial", 12))
        password_entry.pack(pady=(0, 20), padx=50, fill='both', expand=True)

        def on_create():
            username = username_entry.get()
            password = password_entry.get()
            if username and password:  # Basic validation
                self.create_account(username, password)
                account_window.destroy()  # Close the account creation window upon successful account creation
            else:
                messagebox.showerror("Error", "Username and password cannot be empty.")

        create_btn = ttk.Button(account_window, text="Create Account", command=on_create)
        create_btn.pack()

        account_window.grab_set()  # Makes the account window modal

    def create_login_window(self):
        """Create the login window."""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")

        tk.Label(self.login_window, text="Username:", font=("Arial", 12)).pack(pady=5, padx=10, fill='both', expand=True)
        self.username_entry = tk.Entry(self.login_window, font=("Arial", 12))
        self.username_entry.pack(pady=5, padx=10, fill='both', expand=True)

        tk.Label(self.login_window, text="Password:", font=("Arial", 12)).pack(pady=5, padx=10, fill='both', expand=True)
        self.password_entry = tk.Entry(self.login_window, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5, padx=10, fill='both', expand=True)

        ttk.Button(self.login_window, text="Login", command=self.login).pack(pady=5, padx=10, fill='both', expand=True)
        ttk.Button(self.login_window, text="Create Account", command=self.create_account_window).pack(pady=5, padx=10, fill='both', expand=True)

    def login(self):
        """Handle user login."""
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')

        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("SELECT password_hash FROM accounts WHERE username=?", (username,))
        account = c.fetchone()
        
        if account and bcrypt.checkpw(password, account[0]):  # Directly use account[0] which is already a bytes object
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            self.username = username
            self.login_window.destroy()
            self.init_main_app(username)
            self.load_tasks()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
        conn.close()

    def load_tasks(self):
        """Load tasks for the logged-in user."""
        self.task_listbox.delete(0, tk.END)  # Clear the listbox
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("SELECT task, priority, finished FROM tasks WHERE username=?", (self.username,))
        for task in c.fetchall():
            task_text = task[0] + (" [Priority]" if task[1] else "") + (" [Finished]" if task[2] else "")
            self.task_listbox.insert(tk.END, task_text)
        conn.close()

    def create_account(self, username, password):
        """Create a new user account with the given username and password."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO accounts (username, password_hash) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        else:
            messagebox.showinfo("Success", "Account created successfully.")
        finally:
            conn.close()

    def add_task(self):
        """Add a new task for the logged-in user."""
        task = simpledialog.askstring("Add Task", "Task description:")
        if task:  # Check if the task is not empty
            priority = int(self.priority_var.get())
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO tasks (username, task, priority, finished) VALUES (?, ?, ?, 0)",
                      (self.username, task, priority))
            conn.commit()
            conn.close()
            self.load_tasks()  # Refresh the task list

    def edit_task(self):
        """Edit the selected task."""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No task selected.")
            return
        # For simplicity, assume task ID matches listbox index + 1
        # This is a simplification; in a real application, you'd track task IDs separately
        task_id = selection[0] + 1
        new_task = simpledialog.askstring("Edit Task", "New task description:")
        if new_task:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute("UPDATE tasks SET task=? WHERE id=? AND username=?", (new_task, task_id, self.username))
            conn.commit()
            conn.close()
            self.load_tasks()

    def delete_task(self):
        """Delete the selected task."""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No task selected.")
            return
        # Similarly, simplifying task identification
        task_id = selection[0] + 1
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=? AND username=?", (task_id, self.username))
        conn.commit()
        conn.close()
        self.load_tasks()

    def complete_task(self):
        """Mark the selected task as completed."""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No task selected.")
            return
        task_id = selection[0] + 1
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("UPDATE tasks SET finished=1 WHERE id=? AND username=?", (task_id, self.username))
        conn.commit()
        conn.close()
        self.load_tasks()
        
    def delete_account(self, username, password):
        for i, account in enumerate(self.accounts["accounts"]):
            if self.authenticate(account["username"], password):
                del self.accounts["accounts"][i]
                self.save_accounts(self.accounts_file)
                messagebox.showinfo("Success", "Account deleted successfully.")
                return True
        messagebox.showinfo("Error", "Couldn't find account or password")
        return False

    def init_main_app(self, username):
        self.root.title("Todo App")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.username = username
        self.load_tasks()  # Load user-specific tasks

        # Main application window
        self.task_entry = tk.Entry(self.root, font=("Arial", 12))
        self.task_entry.pack(pady=5, padx=50, fill='both')
        
        # Adding search field and filter button
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.root, textvariable=self.search_var, font=("Arial", 12))
        search_entry.pack(pady=5, padx=50, fill='both', expand=True)
        filter_button = ttk.Button(self.root, text="Filter", command=self.filter_tasks)
        filter_button.pack(pady=5, padx=50, fill='both', expand=True)

        ttk.Style().configure("Add.TButton", font=("Arial", 12))
        self.add_button = ttk.Button(self.root, text="Add Task", style="Add.TButton", command=self.add_task)
        self.add_button.pack(pady=5, padx=50, fill='both', expand=True)

        self.priority_var = tk.BooleanVar()
        self.priority_var.set(False)
        tk.Checkbutton(self.root, text="Priority", variable=self.priority_var, font=("Arial", 12), command=self.update_task_list).pack(pady=5, padx=10)

        self.task_listbox = tk.Listbox(self.root, font=("Arial", 12))
        self.task_listbox.pack(pady=5, padx=50, fill='both', expand=1)

        self.edit_button = ttk.Button(self.root, text="Edit Selected Task", style="Add.TButton", command=self.edit_task)
        self.edit_button.pack(pady=5, padx=50, fill='both', expand=True)

        ttk.Style().configure("Complete.TButton", font=("Arial", 12))
        self.complete_button = ttk.Button(self.root, text="Complete Selected Task", style="Complete.TButton", command=self.complete_task)
        self.complete_button.pack(pady=5, padx=50, fill='both', expand=True)

        ttk.Style().configure("Delete.TButton", font=("Arial", 12))  # Configure style for delete button
        self.delete_button = ttk.Button(self.root, text="Delete Task", style="Delete.TButton", command=self.delete_task)
        self.delete_button.pack(pady=5, padx=50, fill='both', expand=True)  # Pack the delete button into the window

        self.update_task_list()

    def filter_tasks(self):
        keyword = self.search_var.get().lower()
        if keyword:
            # Apply filtering only if there is a keyword
            filtered_tasks = [task for task in self.tasks if keyword in task["task"].lower()]
            self.update_task_list(filtered_tasks)
        else:
            # If the keyword is empty, show all tasks
            self.update_task_list(self.tasks)

    def save_tasks(self):
        # Save tasks for the specific user
        for account in self.accounts["accounts"]:
            if account["username"] == self.username:
                account["tasks"] = self.tasks
                break
        self.save_accounts(self.accounts_file)

    def update_task_list(self, tasks=None):
        self.task_listbox.delete(0, tk.END)  # Clear existing tasks in the listbox
        if tasks is None:
            tasks = self.tasks  # If no tasks are provided, use all tasks
        for task in tasks:
            task_text = task["task"] + (" [Priority]" if task["priority"] else "") + (" [Finished]" if task["finished"] else "")
            self.task_listbox.insert(tk.END, task_text)
            if task["priority"]:
                self.task_listbox.itemconfig(tk.END, bg="red")  # Highlight priority tasks

def main():
    root = tk.Tk()
    app = TodoAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()