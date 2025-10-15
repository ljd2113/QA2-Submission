# main_app.py

import tkinter as tk
from db_manager import DBManager
from AdminFunctions import AdminFunctions
from StudentFunctions import StudentFunctions
from tkinter import messagebox
import os # For checking if the database is set up

# Ensure the setup script (from the previous responses) is run at least once
# If you don't have a separate setup script, you can include the logic here.
# For now, let's assume the database is either created or will be created on first run.

# --- Database Setup Check (Optional but Recommended) ---
# To make this runnable, we assume the DB is either there or the setup 
# code from the previous response is run before this, 
# or you include that setup function here.
# If you didn't save the setup script, you must run it before this!
DB_FILE = "ljdialQuizDB.db"
if not os.path.exists(DB_FILE):
    # This is a critical point. If the file is missing, the app will crash.
    # To be safe, ensure the database creation script runs first.
    messagebox.showerror("Setup Error", 
                         f"Database file '{DB_FILE}' not found.\n"
                         "Please run the database creation script once to set up the questions.")
    exit()
# ----------------------------------------------------

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz System - Role Selection")
        self.master.geometry("400x200")
        self.master.resizable(False, False)

        # Initialize the DB Manager - shared by all parts of the application
        self.db_manager = DBManager(db_name=DB_FILE)

        self.create_role_selection_screen()

    def create_role_selection_screen(self):
        """Displays the choice between Admin and Student."""
        tk.Label(self.master, text="Select Your Role:", font=('Arial', 16, 'bold')).pack(pady=20)
        
        tk.Button(self.master, text="Start Quiz (Student)", 
                  command=self.launch_student_quiz, 
                  font=('Arial', 12), width=20, bg='#4CAF50', fg='white').pack(pady=5)
                  
        tk.Button(self.master, text="Admin: Edit Questions", 
                  command=self.launch_admin_panel, 
                  font=('Arial', 12), width=20, bg='#FF9800', fg='black').pack(pady=5)

    def launch_student_quiz(self):
        """Closes the current window and opens the Student Quiz interface."""
        self.master.destroy() 
        quiz_root = tk.Tk()
        StudentFunctions(quiz_root, self.db_manager)
        quiz_root.mainloop()

    def launch_admin_panel(self):
        """Closes the current window and opens the Admin interface."""
        # A simple security check (in a real app, this would be a login screen)
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
        if password == "admin123": # Use a simple hardcoded password for testing
            self.master.destroy() 
            admin_root = tk.Tk()
            AdminFunctions(admin_root, self.db_manager)
            admin_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Incorrect password.")


if __name__ == "__main__":
    # Ensure all required files are present and run the main app
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()