# adminFunctions.py

import tkinter as tk
from tkinter import ttk, messagebox

ADMIN_PASSWORD = "admin" 

class EditQuestionPopup(tk.Toplevel):
    """Popup window for editing a question."""
def __init__(self, parent, db_manager, course_name, question_data, refresh_callback):
        super().__init__(parent)
        self.title("Edit Question")
        self.geometry("500x550")
        self.db_manager = db_manager
        self.course_name = course_name
        self.refresh_callback = refresh_callback
        self.question_id = question_data['id']
        
        self.fields = {}
        
        form_frame = ttk.Frame(self, padding="15")
        form_frame.pack(fill='both', expand=True)

        labels = ['ID:', 'Question Text:', 'Option A:', 'Option B:', 'Option C:', 'Option D:', 'Correct Answer (A, B, C, or D):']
        keys = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        # Determine the simple correct option letter for pre-populating the correct_answer field
        current_correct_text = question_data['correct_answer']
        current_correct_letter = current_correct_text[0].upper() if current_correct_text and len(current_correct_text) > 1 and current_correct_text[1] == ')' else ''

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=3)
            
            if key == 'id':
                ttk.Label(form_frame, text=str(self.question_id)).grid(row=i, column=1, sticky='w', padx=5)
            elif key == 'question':
                entry = tk.Text(form_frame, height=4, width=40)
                entry.insert("1.0", question_data[key])
                entry.grid(row=i, column=1, sticky='ew', pady=3, padx=5)
                self.fields[key] = entry
            else:
                entry = ttk.Entry(form_frame, width=40)
                if key == 'correct_answer':
                    entry.insert(0, current_correct_letter)
                else:
                    entry.insert(0, question_data[key])
                entry.grid(row=i, column=1, sticky='ew', pady=3, padx=5)
                self.fields[key] = entry

        ttk.Button(form_frame, text="Save Changes", command=self.submit_update).grid(row=len(labels), column=0, columnspan=2, pady=15)
        
def submit_update(self):
        """Collects form data and calls the DB manager to update the question."""
        
        # Get data from widgets
        question_data = {
            'id': self.question_id,
            'question': self.fields['question'].get("1.0", tk.END).strip(),
            'option_a': self.fields['option_a'].get().strip(),
            'option_b': self.fields['option_b'].get().strip(),
            'option_c': self.fields['option_c'].get().strip(),
            'option_d': self.fields['option_d'].get().strip(),
            'correct_answer_key': self.fields['correct_answer'].get().strip().upper()
        }
        
        # Simple validation
        if not all(question_data[k] for k in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer_key']):
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
        if question_data['correct_answer_key'] not in ['A', 'B', 'C', 'D']:
            messagebox.showerror("Input Error", "Correct Answer must be A, B, C, or D.")
            return

        # Format the correct_answer string to match the column data (e.g., "A) Option A Text")
        key_to_text = {
            'A': 'option_a', 'B': 'option_b', 'C': 'option_c', 'D': 'option_d'
        }
        correct_key = question_data.pop('correct_answer_key')
        correct_text = question_data[key_to_text[correct_key]]
        question_data['correct_answer'] = f"{correct_key}) {correct_text}"

        # Call DB Manager
        if self.db_manager.update_question(self.course_name, question_data):
            messagebox.showinfo("Success", "Question updated successfully.")
            self.refresh_callback() # Notify the main frame to update the list
            self.destroy() # Close the pop-up
        else:
            messagebox.showerror("Error", "Failed to update question.")

# -------------------------------------------------------------------------------

# --- CLASS 2: ViewEditQuestions (Frame for showing the list of questions) ---

class ViewEditQuestions(ttk.Frame):
    """Admin frame for displaying, editing, and deleting questions."""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.course_names = self.db_manager.get_all_table_names()
        
        # --- Selection/Control Frame ---
        select_frame = ttk.Frame(self)
        select_frame.pack(fill='x', pady=5)
        ttk.Label(select_frame, text="Course:").pack(side=tk.LEFT, padx=5)
        
        self.selected_course = tk.StringVar(self)
        if self.course_names:
            self.selected_course.set(self.course_names[0])
        
        self.course_menu = ttk.Combobox(select_frame, textvariable=self.selected_course, 
                                        values=self.course_names, state="readonly", width=30)
        self.course_menu.pack(side=tk.LEFT, padx=5)
        self.course_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())
        
        # --- Treeview for displaying data ---
        # Frame and Scrollbars
        tree_container = ttk.Frame(self)
        tree_container.pack(fill='both', expand=True, pady=5)
        
        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_container, 
                                 yscrollcommand=tree_scroll_y.set, 
                                 xscrollcommand=tree_scroll_x.set)
        self.tree.pack(fill='both', expand=True)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        self.tree.bind("<<TreeviewSelect>>", self.check_selection)

        # --- Action Buttons ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        self.edit_btn = ttk.Button(btn_frame, text="Edit Selected", command=self.edit_selected, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_data() # Initial load

    def check_selection(self, event):
        """Enables/disables action buttons based on treeview selection."""
        is_selected = bool(self.tree.selection())
        state = tk.NORMAL if is_selected else tk.DISABLED
        self.edit_btn.config(state=state)
        self.delete_btn.config(state=state)

    def refresh_data(self):
        """Fetches and displays data for the currently selected course."""
        course = self.selected_course.get()
        
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not course: return # Skip if no course is selected
        
        questions = self.db_manager.get_all_questions(course)
        
        if not questions:
            self.tree['columns'] = ('ID', 'Question')
            self.tree.heading('ID', text='ID'); self.tree.column('ID', width=50)
            self.tree.heading('Question', text='Question'); self.tree.column('Question', width=700)
            self.tree['show'] = 'headings'
            return

        col_names = list(questions[0].keys())
        self.tree['columns'] = col_names
        self.tree['show'] = 'headings'
        
        for col in col_names:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            width = 50 if col == 'id' else (300 if col == 'question' else 150)
            self.tree.column(col, width=width, anchor='w')

        # Insert data
        for q in questions:
            self.tree.insert('', 'end', values=list(q.values()))
            
    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        
        question_id = self.tree.item(selected_item[0], 'values')[0]
        course_name = self.selected_course.get()

        # Fetch the complete data for the selected ID (as a dict)
        all_questions = self.db_manager.get_all_questions(course_name)
        question_data = next((q for q in all_questions if q['id'] == int(question_id)), None)
        
        if question_data:
            # Pass the current frame's refresh method so the popup can update the list
            EditQuestionPopup(self.master, self.db_manager, course_name, question_data, self.refresh_data)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item: return
        
        question_id = self.tree.item(selected_item[0], 'values')[0]
        course_name = self.selected_course.get()

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Question ID {question_id} from {course_name}?"):
            if self.db_manager.delete_question(course_name, question_id):
                messagebox.showinfo("Success", "Question deleted successfully.")
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to delete question.")

# -------------------------------------------------------------------------------

# --- CLASS 3: AddQuestionFrame (Frame for adding a new question) ---

class AddQuestionFrame(ttk.Frame):
    """Admin frame for adding a new question."""
    
    def __init__(self, parent, db_manager, refresh_callback):
        super().__init__(parent)
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback # Callback to update View/Edit frame
        self.fields = {}
        
        # --- Form Setup ---
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20, padx=20)
        
        # Course Selection
        ttk.Label(form_frame, text="Course:").grid(row=0, column=0, sticky='w', pady=5)
        self.course_var = tk.StringVar(self)
        self.course_combobox = ttk.Combobox(form_frame, textvariable=self.course_var, state="readonly", width=40)
        self.course_combobox.grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        labels = ['Question Text:', 'Option A:', 'Option B:', 'Option C:', 'Option D:', 'Correct Answer (A, B, C, or D):']
        keys = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer_key']

        for i, (label_text, key) in enumerate(zip(labels, keys)):
            ttk.Label(form_frame, text=label_text).grid(row=i+1, column=0, sticky='w', pady=5)
            if key == 'question':
                # Use Text widget for multi-line question
                entry = tk.Text(form_frame, height=4, width=40)
                entry.grid(row=i+1, column=1, sticky='ew', pady=5, padx=5)
            else:
                entry = ttk.Entry(form_frame, width=40)
                entry.grid(row=i+1, column=1, sticky='ew', pady=5, padx=5)
            self.fields[key] = entry
            
        ttk.Button(form_frame, text="Add Question", command=self.submit_question).grid(row=len(labels)+1, column=0, columnspan=2, pady=15)
    
    def load_courses(self):
        """Updates the course combobox with current table names."""
        course_names = self.db_manager.get_all_table_names()
        self.course_combobox['values'] = course_names
        if course_names:
            self.course_var.set(course_names[0])
        else:
            self.course_var.set("")

    def submit_question(self):
        """Collects form data and calls the DB manager to add the question."""
        course = self.course_var.get()
        
        # Get data from widgets
        question_data = {
            'question': self.fields['question'].get("1.0", tk.END).strip(),
            'option_a': self.fields['option_a'].get().strip(),
            'option_b': self.fields['option_b'].get().strip(),
            'option_c': self.fields['option_c'].get().strip(),
            'option_d': self.fields['option_d'].get().strip(),
            'correct_answer_key': self.fields['correct_answer_key'].get().strip().upper()
        }
        
        # Simple validation
        if not all(question_data[k] for k in ['question', 'option_a', 'option_b', 'option_c', 'option_d']) or not course:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
        if question_data['correct_answer_key'] not in ['A', 'B', 'C', 'D']:
            messagebox.showerror("Input Error", "Correct Answer must be A, B, C, or D.")
            return

        # Format correct_answer string (e.g., "A) Option A Text")
        key_to_text = {
            'A': 'option_a', 'B': 'option_b', 'C': 'option_c', 'D': 'option_d'
        }
        correct_key = question_data.pop('correct_answer_key')
        correct_text = question_data[key_to_text[correct_key]]
        question_data['correct_answer'] = f"{correct_key}) {correct_text}"
        
        # Call DB Manager
        if self.db_manager.add_question(course, question_data):
            messagebox.showinfo("Success", "Question added successfully.")
            # Clear fields
            for key in self.fields:
                if key == 'question':
                    self.fields[key].delete("1.0", tk.END)
                else:
                    self.fields[key].delete(0, tk.END)
            self.refresh_callback() # Notify the View/Edit frame to update
        else:
            messagebox.showerror("Error", "Failed to add question to database.")

# -------------------------------------------------------------------------------

# --- CLASS 4: AdminFunctions (The main imported Toplevel for the admin interface) ---

class AdminFunctions(tk.Toplevel):
    """The main Toplevel window for the Admin user."""
    
    # NOTE: The __init__ MUST take 'master' and 'db_manager' when called from main_app.py
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.title("Admin - Quiz Content Management")
        self.geometry("1000x700")
        self.db_manager = db_manager
        
        # Ensure the main app resurfaces when this window closes
        self.protocol("WM_DELETE_WINDOW", self.on_close) 

        self.create_navigation()
        self.create_content_frames()
        self.show_view_edit_frame() # Start on the view/edit screen

    def on_close(self):
        """Called when the admin window is closed."""
        self.master.deiconify()
        self.destroy()

    def create_navigation(self):
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill='x', padx=10, pady=5)
        
        # Navigation Buttons
        ttk.Button(nav_frame, text="View/Edit/Delete Questions", command=self.show_view_edit_frame).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Add New Question", command=self.show_add_question_frame).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Logout", command=self.on_close).pack(side=tk.RIGHT, padx=5)

    def create_content_frames(self):
        # Frame to hold all the different admin view frames (View/Edit, Add)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 1. View/Edit Frame
        self.view_edit_frame = ViewEditQuestions(self.content_frame, self.db_manager)
        self.view_edit_frame.grid(row=0, column=0, sticky="nsew")

        # 2. Add Question Frame
        # The refresh_data call makes sure the view list is updated after a successful add
        self.add_question_frame = AddQuestionFrame(self.content_frame, self.db_manager, self.view_edit_frame.refresh_data)
        self.add_question_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid to allow frames to expand
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def show_view_edit_frame(self):
        self.view_edit_frame.refresh_data() # Refresh data every time we switch to this view
        self.view_edit_frame.tkraise()

    def show_add_question_frame(self):
        self.add_question_frame.load_courses() # Load courses before showing the frame
        self.add_question_frame.tkraise()














