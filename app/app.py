import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import json
import bcrypt
import os

class TodoAppGUI:
    def __init__(self, root, accounts_file="accounts.json"):
        self.root = root
        self.accounts_file = accounts_file
        self.root.title("Todo App")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Initialize task_listbox
        self.task_listbox = None

        # Load accounts from JSON file
        self.accounts = self.load_accounts(self.accounts_file)

        # Create a login window
        self.login_window = tk.Toplevel(root)
        self.login_window.title("Login")

        # Username and password fields
        tk.Label(self.login_window, text="Username:", font=("Arial", 12)).pack(pady=5, padx=10)
        self.username_entry = tk.Entry(self.login_window, font=("Arial", 12))
        self.username_entry.pack(pady=5, padx=10)
        tk.Label(self.login_window, text="Password:", font=("Arial", 12)).pack(pady=5, padx=10)
        self.password_entry = tk.Entry(self.login_window, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5, padx=10)

        # Login and Create Account buttons
        ttk.Style().configure("Login.TButton", font=("Arial", 12))
        ttk.Button(self.login_window, text="Login", style="Login.TButton", command=self.login).pack(pady=5, padx=10)
        ttk.Button(self.login_window, text="Create Account", style="Login.TButton", command=self.create_account_window).pack(pady=5, padx=10)

    def load_accounts(self, filename):
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, "r") as json_file:
                    return json.load(json_file)
            except FileNotFoundError:
                return {"accounts": []}
            except json.decoder.JSONDecodeError:
                return {"accounts": []}
        else:
            return {"accounts": []}

    def save_accounts(self, filename):
        with open(filename, "w") as json_file:
            json.dump(self.accounts, json_file, indent=4)

    def login(self, username=None, password=None):
        # If username and password are not provided, use the GUI elements
        if username is None or password is None:
            username = self.username_entry.get()
            password = self.password_entry.get()
        
        # Proceed with your existing login logic
        if self.authenticate(username, password):
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            self.login_window.destroy()  # Close the login window
            self.init_main_app(username)  # Initialize the main application window
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def authenticate(self, username, password):
        # Check if the provided username and password match any account
        for account in self.accounts["accounts"]:
            if account["username"] == username:
                stored_password_hash = account["password_hash"].encode('utf-8')
                entered_password = password.encode('utf-8')
                if bcrypt.checkpw(entered_password, stored_password_hash):
                    return True
                break
        return False

    def create_account_window(self):
        # Create a new window for creating an account
        create_account_window = tk.Toplevel(self.root)
        create_account_window.title("Create Account")

        # Username and password fields
        tk.Label(create_account_window, text="Username:", font=("Arial", 12)).pack(pady=5, padx=10)
        username_entry = tk.Entry(create_account_window, font=("Arial", 12))
        username_entry.pack(pady=5, padx=10)
        tk.Label(create_account_window, text="Password:", font=("Arial", 12)).pack(pady=5, padx=10)
        password_entry = tk.Entry(create_account_window, show="*", font=("Arial", 12))
        password_entry.pack(pady=5, padx=10)

        # Create Account button
        ttk.Style().configure("Create.TButton", font=("Arial", 12))
        ttk.Button(create_account_window, text="Create Account", style="Create.TButton",
                command=lambda: self.create_account(username_entry.get(), password_entry.get())).pack(pady=5, padx=10)

        # Delete Account button
        ttk.Style().configure("Delete.TButton", font=("Arial", 12))
        ttk.Button(create_account_window, text="Delete Account", style="Delete.TButton",
                command=lambda: self.delete_account(username_entry.get(), password_entry.get())).pack(pady=5, padx=10)

    def create_account(self, username, password):
        for account in self.accounts["accounts"]:
            if account["username"] == username:
                messagebox.showerror("Error", "Username already exists.")
                return
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.accounts["accounts"].append({"username": username, "password_hash": hashed_password, "tasks": []})
        self.save_accounts(self.accounts_file)
        messagebox.showinfo("Success", "Account created successfully.")
        self.create_account_window.destroy()  # Close the login window

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
        self.username = username
        self.load_tasks()  # Load user-specific tasks

        # Main application window
        self.task_entry = tk.Entry(self.root, font=("Arial", 12))
        self.task_entry.pack(pady=5, padx=50, fill='both')
        
        # Adding search field and filter button
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.root, textvariable=self.search_var, font=("Arial", 12))
        search_entry.pack(pady=5)
        filter_button = ttk.Button(self.root, text="Filter", command=self.filter_tasks)
        filter_button.pack(pady=5)

        ttk.Style().configure("Add.TButton", font=("Arial", 12))
        self.add_button = ttk.Button(self.root, text="Add Task", style="Add.TButton", command=self.add_task)
        self.add_button.pack(pady=5, padx=10)

        self.priority_var = tk.BooleanVar()
        self.priority_var.set(False)
        tk.Checkbutton(self.root, text="Priority", variable=self.priority_var, font=("Arial", 12), command=self.update_task_list).pack(pady=5, padx=10)

        self.task_listbox = tk.Listbox(self.root, font=("Arial", 12))
        self.task_listbox.pack(pady=5, padx=50, fill='both', expand=1)

        self.edit_button = ttk.Button(self.root, text="Edit Selected Task", style="Add.TButton", command=self.edit_task)
        self.edit_button.pack(pady=5, padx=10)

        ttk.Style().configure("Complete.TButton", font=("Arial", 12))
        self.complete_button = ttk.Button(self.root, text="Complete Selected Task", style="Complete.TButton", command=self.complete_task)
        self.complete_button.pack(pady=5, padx=10)

        ttk.Style().configure("Delete.TButton", font=("Arial", 12))  # Configure style for delete button
        self.delete_button = ttk.Button(self.root, text="Delete Task", style="Delete.TButton", command=self.delete_task)
        self.delete_button.pack(pady=5, padx=10)  # Pack the delete button into the window

        self.update_task_list()

    def load_tasks(self):
        # Load tasks for the specific user
        for account in self.accounts["accounts"]:
            if account["username"] == self.username:
                self.tasks = account.get("tasks", [])
                break

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

    def add_task(self, task=None):
        if task is None:
            task = self.task_entry.get()
        if task:
            priority = self.priority_var.get()
            self.tasks.append({"task": task, "priority": priority, "finished": False})  # Add task with finished status
            self.save_tasks()  # Save tasks
            self.update_task_list()
            self.task_entry.delete(0, tk.END)

    def edit_task(self, new_task=None):
        selected_index = self.task_listbox.curselection()
        if selected_index is not None and len(selected_index) > 0:
            index = selected_index[0]
            old_task = self.tasks[index]["task"]
            old_priority = self.tasks[index]["priority"]
            new_task = simpledialog.askstring("Edit Task", "New Task:", initialvalue=old_task)
            if new_task is not None:
                new_priority = messagebox.askyesno("Edit Priority", "Set task priority?")
                self.tasks[index]["task"] = new_task
                self.tasks[index]["priority"] = new_priority
                self.save_tasks()  # Save tasks
                self.update_task_list()
        else:
            raise ValueError("No task selected for editing")

    def update_task_list(self, tasks=None):
        self.task_listbox.delete(0, tk.END)  # Clear existing tasks in the listbox
        if tasks is None:
            tasks = self.tasks  # If no tasks are provided, use all tasks
        for task in tasks:
            task_text = task["task"] + (" [Priority]" if task["priority"] else "") + (" [Finished]" if task["finished"] else "")
            self.task_listbox.insert(tk.END, task_text)
            if task["priority"]:
                self.task_listbox.itemconfig(tk.END, bg="red")  # Highlight priority tasks

    def complete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.tasks[index]["finished"] = True  # Mark task as finished
            
            # Save the updated task list for the current user
            for account in self.accounts["accounts"]:
                if account["username"] == self.username:
                    account["tasks"] = self.tasks
                    break
            self.save_accounts(self.accounts_file)  # Persist changes
            
            self.update_task_list()  # Reflect changes in the UI
            return index  # For testing purposes
        return None

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            del self.tasks[index]  # Remove the selected task from the list
            self.update_task_list()  # Update the task listbox display
            self.save_tasks()  # Save the updated tasks to the file
            return index  # Return the index of the deleted task
        return None


def main():
    root = tk.Tk()
    app = TodoAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
