import sqlite3
import bcrypt
from crypt import encrypt_data, decrypt_data

DATABASE_NAME = "todo_app.db"

def initialize_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS accounts
                     (username TEXT PRIMARY KEY, password_hash TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY, username TEXT, task TEXT, 
                      priority INTEGER, finished INTEGER,
                      FOREIGN KEY(username) REFERENCES accounts(username))''')
        conn.commit()

def create_account(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO accounts (username, password_hash) VALUES (?, ?)", 
                      (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def check_login(username, password):
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM accounts WHERE username=?", (username,))
        account = c.fetchone()
        if account and bcrypt.checkpw(password.encode('utf-8'), account[0]):
            return True
        else:
            return False

def add_task(username, task, priority, password):
    encrypted_task = encrypt_data(task, password)
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (username, task, priority, finished) VALUES (?, ?, ?, 0)",
                  (username, encrypted_task, priority))
        conn.commit()

def fetch_tasks(username, password):
    tasks = []
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, task, priority, finished FROM tasks WHERE username=?", (username,))
        encrypted_tasks = c.fetchall()
        for task in encrypted_tasks:
            decrypted_task = list(task)
            decrypted_task[1] = decrypt_data(task[1], password)  # Decrypt task description
            tasks.append(decrypted_task)
    return tasks

def update_task(task_id, username, new_task_description, priority, finished, password):
    """
    Update an existing task with new details.
    """
    encrypted_task = encrypt_data(new_task_description, password)
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET task=?, priority=?, finished=? WHERE id=? AND username=?", (encrypted_task, priority, finished, task_id, username))
        conn.commit()

def complete_task(task_id, username, password):
    """
    Mark a task as completed.
    """
    # Fetch the current task to re-encrypt it, as its encryption might depend on mutable data like 'finished' status if included in encryption.
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT task FROM tasks WHERE id=? AND username=?", (task_id, username))
        task_row = c.fetchone()
        if task_row:
            # Re-encrypt the task with the updated 'finished' status.
            encrypted_task = encrypt_data(decrypt_data(task_row[0], password), password)
            c.execute("UPDATE tasks SET finished=1, task=? WHERE id=? AND username=?", (encrypted_task, task_id, username))
            conn.commit()

def uncomplete_task(task_id, username, password):
    """
    Mark a task as not completed.
    """
    # Similar logic to `complete_task` but marking the task as not finished.
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT task FROM tasks WHERE id=? AND username=?", (task_id, username))
        task_row = c.fetchone()
        if task_row:
            encrypted_task = encrypt_data(decrypt_data(task_row[0], password), password)
            c.execute("UPDATE tasks SET finished=0, task=? WHERE id=? AND username=?", (encrypted_task, task_id, username))
            conn.commit()

def edit_task(task_id, username, new_task_description, priority, password):
    """
    Edit the description and priority of an existing task.
    """
    encrypted_task = encrypt_data(new_task_description, password)
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET task=?, priority=? WHERE id=? AND username=?", (encrypted_task, priority, task_id, username))
        conn.commit()

def delete_task(id, username):
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=? AND username=?", (id, username))
        conn.commit()

def delete_account(username):
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE username=?", (username,))  # Delete user's tasks first due to FK constraint
        c.execute("DELETE FROM accounts WHERE username=?", (username,))
        conn.commit()