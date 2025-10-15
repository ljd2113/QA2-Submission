import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

# ✅ Use your renamed DB module
from databaseSetup import ensure_db_ready, list_courses

APP_TITLE = "Welcome. Choose your login"
ADMIN_PASSWORD = "admin"

def launch(script_name: str, *args: str) -> None:
    """
    Launch another Python script in a separate process.
    Ensures it runs from the same folder as this file.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(here, script_name)
    if not os.path.exists(script_path):
        messagebox.showerror("Missing file", f"Could not find: {script_name}")
        return
    subprocess.Popen([sys.executable, script_path, *args])

def on_admin_login() -> None:
    pw = pw_entry.get().strip()
    if pw == ADMIN_PASSWORD:
        launch("adminApp.py")
    else:
        messagebox.showerror("Access denied", "Wrong password.")

def show_student_courses() -> None:
    # Replace the current view with the course picker
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Pick a course", font=("Arial", 14, "bold")).pack(pady=10)

    try:
        courses = list_courses()  # from databaseSetup
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load courses.\n{e}")
        return

    if not courses:
        messagebox.showwarning("No courses", "No courses found in the database.")
        return

    for c in courses:
        tk.Button(root, text=c, width=32,
                  command=lambda name=c: launch("student_quiz.py", name)).pack(pady=6)

    # Add a small back button to return to login screen
    tk.Button(root, text="⬅ Back", command=render_login_screen).pack(pady=8)

def render_login_screen() -> None:
    for w in root.winfo_children():
        w.destroy()

    tk.Label(root, text="Login", font=("Arial", 16, "bold")).pack(pady=12)

    row = tk.Frame(root); row.pack(pady=8)
    tk.Label(row, text="Admin Password:").grid(row=0, column=0, padx=5, pady=4, sticky="e")

    global pw_entry
    pw_entry = tk.Entry(row, show="*")
    pw_entry.grid(row=0, column=1, padx=5, pady=4)

    tk.Button(row, text="Admin Login", width=14, command=on_admin_login)\
        .grid(row=0, column=2, padx=5, pady=4)

    tk.Label(root, text="OR", font=("Arial", 12)).pack(pady=4)
    tk.Button(root, text="Student → Choose Course", width=28, command=show_student_courses)\
        .pack(pady=2)

# --- App init ---
# Make sure the DB exists & is seeded before any UI interaction
try:
    ensure_db_ready()   # from databaseSetup
except Exception as e:
    # If seeding fails, show a clear message
    messagebox.showerror("Database Error",
                         f"Failed to initialize database.\n\n{e}\n\n"
                         f"Try running: python databaseSetup.py")
    raise

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("400x240")

# Build initial login view
pw_entry = None  # will be set in render_login_screen()
render_login_screen()

root.mainloop()
