import unittest
from test_app import TodoAppGUI  # Import your main application class
import tkinter as tk
import os
import json

# Assuming your TodoAppGUI class is modified to accept a filename for the accounts storage,
# so you can use a test file instead of the real one during tests.

class TestTodoAppGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_accounts_file = "test_accounts.json"
        with open(cls.test_accounts_file, "w") as f:
            json.dump({"accounts": []}, f)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_accounts_file)

    def setUp(self):
        self.root = tk.Tk()
        self.app = TodoAppGUI(self.root, self.test_accounts_file)
        # Reset the test_accounts.json file to an empty state
        with open(self.test_accounts_file, "w") as f:
            json.dump({"accounts": []}, f)

    def tearDown(self):
        # This ensures the Tkinter window is destroyed after each test
        self.root.destroy()

    def test_account_creation_and_login(self):
        # Test both account creation and login functionality in one go
        username = "testuser"
        password = "password123"
        self.app.create_account(username, password)
        
        # Check if the account is created
        self.assertTrue(self.app.authenticate(username, password))

        # Cleanup by removing the created account
        with open(self.test_accounts_file, "r+") as f:
            data = json.load(f)
            data["accounts"] = [acc for acc in data["accounts"] if acc["username"] != username]
            f.seek(0)
            f.truncate()
            json.dump(data, f)

    def test_add_task(self):
        username = "testuser"
        password = "password123"
        task = "Do laundry"
        self.app.create_account(username, password)  # Ensure you have logic to handle account creation for tests

        # Now directly use the modified login method
        self.app.login(username, password)
        self.app.add_task(task)
        
        # Check if the task was added
        self.assertIn(task, [t["task"] for t in self.app.tasks])
            
    def test_complete_task(self):
        # Test completing a task visually
        username = "testuser"
        password = "password123"
        task = "Do laundry"
        self.app.create_account(username, password)  # Ensure you have logic to handle account creation for tests

        # Now directly use the modified login method
        self.app.login(username, password)
        self.app.add_task(task)
        self.app.task_listbox.selection_set(0)  # Select the first task
        completed_task_index = self.app.complete_task()

        # Check if the task is visually marked as completed
        self.assertIsNotNone(completed_task_index)
        self.assertTrue(self.app.tasks[completed_task_index]["finished"])

    def test_delete_task(self):
        # Test deleting a task visually
        username = "testuser"
        password = "password123"
        task = "Do laundry"
        self.app.create_account(username, password)  # Ensure you have logic to handle account creation for tests

        # Now directly use the modified login method
        self.app.login(username, password)
        self.app.add_task(task)
        self.app.task_listbox.selection_set(0)  # Select the first task
        initial_task_count = self.app.task_listbox.size()
        deleted_task_index = self.app.delete_task()

        # Check if the task is visually deleted
        self.assertIsNotNone(deleted_task_index)
        updated_task_count = self.app.task_listbox.size()
        self.assertEqual(updated_task_count, initial_task_count - 1)

    def test_edit_task(self):
        # Test editing a task visually
        username = "testuser"
        password = "password123"
        original_task = "Do laundry"
        edited_task = "Fold laundry"
        self.app.create_account(username, password)  # Ensure you have logic to handle account creation for tests

        # Now directly use the modified login method
        self.app.login(username, password)
        self.app.add_task(original_task)
        self.app.task_listbox.selection_clear(0, tk.END)  # Ensure no task is selected

        with self.assertRaises(ValueError):
            self.app.edit_task(edited_task)

    def test_delete_account(self):
        # Test deleting an account
        username = "testuser"
        password = "password123"
        self.app.create_account(username, password)  # Create a test account

        # Attempt to delete the account
        self.assertTrue(self.app.delete_account(username, password))

        # Check if the account was deleted by attempting to log in
        self.assertFalse(self.app.authenticate(username, password))

    def test_delete_account(self):
        username = "deletable_user"
        password = "test_password"
        self.app.create_account(username, password)
        self.assertTrue(self.app.authenticate(username, password), "Account should exist after creation")
        self.assertTrue(self.app.delete_account(username, password), "Account deletion should succeed")
        self.assertFalse(self.app.authenticate(username, password), "Account should not exist after deletion")

    def test_user_data_isolation(self):
        # Create accounts and a task for user 1
        user1, password1 = "user1", "password123"
        user2, password2 = "user2", "password456"
        self.app.create_account(user1, password1)
        self.app.login(user1, password1)
        task1 = "User 1's private task"
        self.app.add_task(task1)

        # Simulate logging out user1 and then logging in as user2
        self.app.username = None
        self.app.tasks = []
        self.app.login(user2, password2)

        # User 2 should not see User 1's task
        user2_tasks = [task["task"] for task in self.app.tasks]
        self.assertNotIn(task1, user2_tasks, "User 2 should not access User 1's task.")

    def test_task_completion_persistence(self):
        username = "testuser_completion"
        password = "password"
        self.app.create_account(username, password)
        self.app.login(username, password)
        
        task = "Complete me"
        self.app.add_task(task)
        self.app.task_listbox.selection_set(0)  # Select the task
        self.app.complete_task()  # Mark it as completed
        
        # Re-load the app to simulate a new session and verify task completion persists
        self.setUp()  # Re-initialize the app and login window
        self.app.login(username, password)
        
        self.assertTrue(self.app.tasks[0]["finished"], "Task should be marked as completed across sessions.")

    def test_task_deletion_persistence(self):
        username = "testuser_deletion"
        password = "password"
        self.app.create_account(username, password)
        self.app.login(username, password)
        
        task = "Delete me"
        self.app.add_task(task)
        self.app.task_listbox.selection_set(0)  # Select the task
        self.app.delete_task()  # Delete the task
        
        # Re-load the app to simulate a new session and verify task deletion persists
        self.setUp()  # Re-initialize the app and login window
        self.app.login(username, password)
        
        self.assertEqual(len(self.app.tasks), 0, "Tasks should be deleted across sessions.")

    def test_account_deletion_and_data_isolation(self):
        username = "testuser_account_deletion"
        password = "password"
        self.app.create_account(username, password)
        self.app.login(username, password)
        
        task = "Task for deletion"
        self.app.add_task(task)  # Add a task to ensure it's also deleted
        
        # Delete the account
        self.assertTrue(self.app.delete_account(username, password), "Account deletion should succeed.")
        
        # Attempt to login to the deleted account
        login_success = self.app.login(username, password)
        self.assertFalse(login_success, "Should not be able to log in with a deleted account.")
        
        # Re-load the app to simulate a new session and verify the account and tasks are completely removed
        self.setUp()  # Re-initialize the app and login window
        self.assertFalse(self.app.authenticate(username, password), "Deleted account should not exist.")

    def test_filter_tasks_with_keyword(self):
        username = "testuser_filter"
        password = "testpassword"
        self.app.create_account(username, password)
        self.app.login(username, password)
        
        # Add tasks for testing the filter
        self.app.add_task("Buy milk")
        self.app.add_task("Read a book")
        self.app.add_task("Buy coffee")
        
        # Set the search keyword to filter tasks
        self.app.search_var.set("buy")
        self.app.filter_tasks()
        
        # Verify that only tasks containing "buy" are displayed
        displayed_tasks = [self.app.task_listbox.get(idx) for idx in range(self.app.task_listbox.size())]
        self.assertIn("Buy milk", displayed_tasks)
        self.assertIn("Buy coffee", displayed_tasks)
        self.assertNotIn("Read a book", displayed_tasks)

    def test_filter_tasks_empty_keyword_shows_all_tasks(self):
        username = "testuser_all_tasks"
        password = "password123"
        self.app.create_account(username, password)
        self.app.login(username, password)
        
        # Add tasks
        tasks_to_add = ["Buy milk", "Read a book", "Buy coffee"]
        for task in tasks_to_add:
            self.app.add_task(task)
        
        # Make sure the UI is updated to reflect added tasks
        self.app.update_task_list()  # Refresh the task listbox if necessary
        
        # Clear the search keyword to show all tasks
        self.app.search_var.set("")
        self.app.filter_tasks()
        
        # Check the displayed tasks against expected
        displayed_tasks = [self.app.task_listbox.get(idx) for idx in range(self.app.task_listbox.size())]
        self.assertEqual(len(displayed_tasks), len(tasks_to_add), "All tasks should be displayed when filter is cleared.")

if __name__ == '__main__':
    unittest.main()
