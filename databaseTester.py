import tkinter as tk
from tkinter import ttk
import sqlite3

# --- Configuration ---
DATABASE_FILE = 'ljdialQuizDB.db' # <--- CONFIRMED DB FILE NAME

def get_table_names():
    """Connects to the database and returns a list of all table names."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # Query the special sqlite_master table to get all non-system table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def get_table_data(table_name):
    """Fetches all column names and data from a specified table."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # Fetch data
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        # Get column names (descriptions are returned as tuples)
        column_names = [description[0] for description in cursor.description]
        
        conn.close()
        return column_names, data
    except sqlite3.Error as e:
        # Handle cases where the table name might be invalid or the database is locked
        print(f"Error fetching data for table '{table_name}': {e}")
        return [], []

class QuizDatabaseViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz Database Viewer")
        self.geometry("1000x700") # Larger window to accommodate wide question data

        # Get the list of tables
        self.table_names = get_table_names()

        if not self.table_names:
            tk.Label(self, text=f"No tables found in '{DATABASE_FILE}'. Ensure the file exists.", 
                     fg="red").pack(pady=20)
            return

        # --- Table Selection Frame ---
        
        select_frame = ttk.Frame(self)
        select_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(select_frame, text="Select Quiz Table:").pack(side=tk.LEFT, padx=5)

        # Dropdown (Combobox) for table selection
        self.selected_table = tk.StringVar(self)
        self.selected_table.set(self.table_names[0]) # Set initial table selection
        
        table_menu = ttk.Combobox(select_frame, textvariable=self.selected_table, 
                                  values=self.table_names, state="readonly")
        table_menu.pack(side=tk.LEFT, padx=5, expand=True, fill='x')
        # Bind the update function to the selection event
        table_menu.bind("<<ComboboxSelected>>", self.display_table_data)

        # --- Treeview Display Frame ---
        
        # Frame for the Treeview and its scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Treeview widget (The table)
        self.data_tree = ttk.Treeview(tree_frame, 
                                     yscrollcommand=tree_scroll_y.set, 
                                     xscrollcommand=tree_scroll_x.set)
        self.data_tree.pack(fill='both', expand=True)

        # Configure scrollbars to communicate with the Treeview
        tree_scroll_y.config(command=self.data_tree.yview)
        tree_scroll_x.config(command=self.data_tree.xview)
        
        # Initial data load
        self.display_table_data()

    def display_table_data(self, event=None):
        """Clears the existing Treeview and displays data for the selected table."""
        table_name = self.selected_table.get()
        column_names, data = get_table_data(table_name)

        # 1. Clear previous data
        for row in self.data_tree.get_children():
            self.data_tree.delete(row)
        
        # 2. Reconfigure columns
        self.data_tree['columns'] = column_names
        self.data_tree['show'] = 'headings' # Show column headings

        # Setup column headings and intelligent widths
        for col_name in column_names:
            self.data_tree.heading(col_name, text=col_name)
            # Set specific widths for better viewing of quiz data
            if col_name == 'id':
                width = 30
            elif col_name == 'question':
                width = 300
            else:
                width = 150 # For options and correct_answer
            self.data_tree.column(col_name, width=width, anchor='w')

        # 3. Insert new data
        for row in data:
            self.data_tree.insert('', 'end', values=row)

# --- Run the application ---
if __name__ == "__main__":
    app = QuizDatabaseViewer()
    app.mainloop()