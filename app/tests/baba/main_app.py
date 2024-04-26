import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from database import fetch_tasks, add_task, edit_task, complete_task, uncomplete_task, delete_task, delete_account

class MainApp:
    def __init__(self, root, username, password):
        self.root = root
        self.username = username
        self.password = password  # Storing password securely for future use
        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        self.root.title(f"Todo App - {self.username}")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Priority selection
        self.priority_var = tk.IntVar()
        tk.Checkbutton(self.root, text="High Priority", variable=self.priority_var).pack(pady=2)

        # Task entry and Add Task button
        self.task_entry = tk.Entry(self.root, font=("Arial", 12))
        self.task_entry.pack(pady=5, padx=50, fill='x')
        add_task_button = ttk.Button(self.root, text="Add Task", command=self.add_new_task)
        add_task_button.pack(pady=5, padx=50)

        # Filter field
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(self.root, textvariable=self.filter_var, font=("Arial", 12))
        self.filter_entry.pack(pady=5, padx=50)
        filter_button = ttk.Button(self.root, text="Filter Tasks", command=self.filter_tasks)
        filter_button.pack(pady=2, padx=50)

        # Task list display
        self.task_listbox = tk.Listbox(self.root, font=("Arial", 12), height=15)
        self.task_listbox.pack(pady=5, padx=50, fill='both', expand=True)

        # Task operation buttons
        edit_task_button = ttk.Button(self.root, text="Edit Selected Task", command=self.edit_selected_task)
        edit_task_button.pack(side=tk.LEFT, pady=5, padx=10)

        complete_task_button = ttk.Button(self.root, text="Complete Selected Task", command=self.complete_selected_task)
        complete_task_button.pack(side=tk.LEFT, pady=5, padx=10)

        delete_task_button = ttk.Button(self.root, text="Delete Selected Task", command=self.delete_selected_task)
        delete_task_button.pack(side=tk.LEFT, pady=5, padx=10)

        delete_account_button = ttk.Button(self.root, text="Delete Account", command=self.delete_current_account)
        delete_account_button.pack(pady=20)

    def add_new_task(self):
        task_description = self.task_entry.get()
        priority = self.priority_var.get()
        if task_description:
            add_task(self.username, task_description, priority, self.password)
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showinfo("Info", "Task description cannot be empty.")

    def load_tasks(self):
        self.tasks = fetch_tasks(self.username, self.password)
        self.display_tasks()

    def display_tasks(self, tasks=None):
        if tasks:
            self.tasks = tasks
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            display_text = f"{task[1]} - {'High' if task[2] else 'Low'} Priority - {'Completed' if task[3] else 'Pending'}"
            self.task_listbox.insert(tk.END, display_text)

    def complete_selected_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task_id = self.task_listbox.curselection()[0] + 1  # Simplification
            current_status = self.tasks[selection[0]][3]  # Assuming 3rd index is 'finished' status
            new_status = 0 if current_status else 1
            if (new_status):
                complete_task(task_id, self.username, self.password)
            else:
                uncomplete_task(task_id, self.username, self.password)
            self.load_tasks()

    def edit_selected_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task_id = self.task_listbox.curselection()[0] + 1
            new_description = simpledialog.askstring("Edit Task", "New task description:")
            if new_description is not None:
                new_priority = messagebox.askyesno("Edit Task", "Is this a high-priority task?")
                edit_task(task_id, self.username, new_description, int(new_priority), self.password)
                self.load_tasks()

    def delete_selected_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task_id = self.task_listbox.curselection()[0] + 1
            delete_task(task_id, self.username)
            self.load_tasks()

    def delete_current_account(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete your account? All data will be lost."):
            delete_account(self.username)
            self.root.destroy()

    def filter_tasks(self):
        keyword = self.filter_var.get().lower()
        filtered_tasks = [task for task in fetch_tasks(self.username, self.password) if keyword in task[1].lower()]
        self.display_tasks(filtered_tasks)