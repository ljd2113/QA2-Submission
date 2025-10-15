# main_app.py
from tkinter import simpledialog
import tkinter as tk
from db_manager import DBManager 
from AdminFunctions import AdminFunctions 
from StudentFunctions import StudentFunctions 
from tkinter import messagebox
import os 

# --- Database Configuration ---
DB_FILE = "ljdialQuizDB.db"

class MainApplication:
    """The main application window that handles role selection and database initialization."""
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz System - Role Selection")
        self.master.minsize(400, 200) 
        self.master.resizable(False, False)

        # Initialize the DB Manager - shared by all parts of the application
        # NOTE: DBManager must be available via import
        self.db_manager = DBManager(db_name=DB_FILE)

        # Initial check for database file
        if not os.path.exists(DB_FILE):
            messagebox.showerror("Setup Error", 
                                 f"Database file '{DB_FILE}' not found.\n"
                                 "Please ensure the database creation script has been run.")
            self.master.destroy() 
            return

        self.create_role_selection_screen()
        
    def show_main_window(self):
        """Method called by Toplevel windows to bring the main window back."""
        self.master.deiconify() # Re-show the hidden window
        self.master.lift()      # Bring it to the front
        
    def hide_main_window(self):
        """Method to hide the main window when a sub-window opens."""
        self.master.withdraw()

    def create_role_selection_screen(self):
        """Displays the choice between Admin and Student."""
        role_frame = tk.Frame(self.master)
        role_frame.pack(pady=20, padx=20, expand=True) 
        
        tk.Label(role_frame, text="Select Your Role:", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # --- STUDENT BUTTON ---
        tk.Button(
            role_frame, 
            text="Start Quiz (Student)", 
            command=self.launch_student_quiz, 
            font=('Arial', 12), 
            width=25, 
            bg='#4CAF50', 
            fg='white'
        ).pack(pady=5)
        
        # --- ADMINISTRATOR BUTTON ---
        tk.Button(
            role_frame, 
            text="Administrator", 
            command=self.open_admin_login,
            font=('Arial', 12), 
            width=25, 
            bg='#FF9900', 
            fg='black'
        ).pack(pady=5)

    def launch_student_quiz(self):
        """Hides the main window and launches the Student Quiz interface."""
        self.hide_main_window() 
        # Pass the callback function (self.show_main_window) to StudentFunctions
        StudentFunctions(self.master, self.db_manager, self.show_main_window) 

    def open_admin_login(self):
        """Handles admin password prompt and launches Admin interface."""
        ADMIN_PASSWORD = "admin" 
        
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show='*')
        
        if password == ADMIN_PASSWORD: 
            self.hide_main_window() 
            # Pass the callback function (self.show_main_window) to AdminFunctions
            AdminFunctions(self.master, self.db_manager, self.show_main_window)
        elif password is not None:
            messagebox.showerror("Login Failed", "Incorrect password.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()