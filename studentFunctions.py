No problem! I'll resend the complete and corrected code for studentFunctions.py. The non-code text has been removed, so this version is ready to copy and paste directly into your file.

Save this as studentFunctions.py.

Python

# studentFunctions.py

import tkinter as tk
from tkinter import ttk, messagebox
import random

class StudentInterface(tk.Toplevel):
    """The student interface for selecting and taking a quiz."""
    
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.title("Student - Take Quiz")
        self.geometry("700x500")
        self.db_manager = db_manager
        self.protocol("WM_DELETE_WINDOW", self.on_close) 

        self.all_courses = self.db_manager.get_all_table_names()
        
        # Quiz state variables
        self.current_questions = []
        self.question_index = 0
        self.score = 0
        self.selected_answer = tk.StringVar()

        self.create_widgets()

    def on_close(self):
        """Called when the student window is closed."""
        self.master.deiconify()
        self.destroy()

    def create_widgets(self):
        # --- Welcome/Selection Screen ---
        self.welcome_frame = ttk.Frame(self, padding="20")
        self.welcome_frame.pack(fill='both', expand=True)

        ttk.Label(self.welcome_frame, text="Select a Quiz Category", font=('Arial', 18, 'bold')).pack(pady=20)
        
        # Course Selection
        self.course_var = tk.StringVar(self)
        self.course_var.set("Choose Course") 
        
        # Dropdown for category selection
        course_menu = ttk.Combobox(self.welcome_frame, textvariable=self.course_var, 
                                   values=self.all_courses, state="readonly", width=40)
        course_menu.pack(pady=10)

        ttk.Button(self.welcome_frame, text="Start Quiz", command=self.start_quiz).pack(pady=20)
        ttk.Button(self.welcome_frame, text="Back to Login", command=self.on_close).pack(pady=10)

        # --- Quiz Frame (will be displayed later) ---
        self.quiz_frame = ttk.Frame(self, padding="20")
        
    def start_quiz(self):
        """Loads questions, shuffles them, and switches to the quiz frame."""
        selected_course = self.course_var.get()
        if selected_course not in self.all_courses:
            messagebox.showerror("Error", "Please select a valid course to start the quiz.")
            return
            
        # 1. Fetch and Shuffle Questions
        self.current_questions = self.db_manager.get_all_questions(selected_course)
        random.shuffle(self.current_questions)
        
        if not self.current_questions:
            messagebox.showinfo("Quiz Empty", "No questions available for this course.")
            return

        # 2. Reset State
        self.question_index = 0
        self.score = 0
        
        # 3. Switch View
        self.welcome_frame.pack_forget()
        self.quiz_frame.pack(fill='both', expand=True)
        self.display_question()

    def display_question(self):
        """Displays the current question and its options."""
        # Check if the quiz is over
        if self.question_index >= len(self.current_questions):
            self.show_results()
            return

        # Clear previous content
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        current_q = self.current_questions[self.question_index]
        
        # --- Question Display ---
        q_label = ttk.Label(self.quiz_frame, 
                            text=f"Question {self.question_index + 1}/{len(self.current_questions)}:\n\n{current_q['question']}", 
                            font=('Arial', 12), wraplength=650, justify=tk.LEFT)
        q_label.pack(pady=20, anchor='w')

        # --- Options ---
        options = [
            ('A', current_q['option_a']), 
            ('B', current_q['option_b']), 
            ('C', current_q['option_c']), 
            ('D', current_q['option_d'])
        ]
        
        self.selected_answer.set("") # Clear previous selection
        
        for value, text in options:
            # The value we store is the option text itself (e.g., "Microsoft Excel")
            display_text = f"{value}) {text}"
            rb = ttk.Radiobutton(self.quiz_frame, text=display_text, variable=self.selected_answer, 
                                 value=text, command=self.enable_submit)
            rb.pack(pady=5, anchor='w')

        # --- Submit/Next Button ---
        self.submit_btn = ttk.Button(self.quiz_frame, text="Submit Answer", command=self.submit_answer, state=tk.DISABLED)
        self.submit_btn.pack(pady=20)
        
        # --- Score Tracker ---
        ttk.Label(self.quiz_frame, text=f"Current Score: {self.score}", foreground='blue').pack(side=tk.BOTTOM, pady=5)

    def enable_submit(self):
        """Enables the submit button once an option is selected."""
        self.submit_btn.config(state=tk.NORMAL)

    def submit_answer(self):
        """Checks the answer, provides feedback, and moves to the next question."""
        user_answer_text = self.selected_answer.get()
        current_q = self.current_questions[self.question_index]
        correct_answer_formatted = current_q['correct_answer']
        
        # Extract the correct option text from the formatted string (e.g., extracts "Option A Text" from "A) Option A Text")
        try:
            # Split by the first ')' and take the second part (the text)
            correct_option_text = correct_answer_formatted.split(')', 1)[1].strip()
        except IndexError:
            # Fallback if data is corrupted, use the full formatted string
            correct_option_text = correct_answer_formatted.strip()
            
        
        is_correct = (user_answer_text == correct_option_text)

        # Disable the submit button and options after submission
        self.submit_btn.config(state=tk.DISABLED)

        # 1. Check Answer and Update Score
        if is_correct:
            self.score += 1
            feedback_msg = "Correct! 🎉"
        else:
            feedback_msg = f"Incorrect. The correct answer was: {correct_answer_formatted}"

        # 2. Provide Immediate Feedback
        messagebox.showinfo("Feedback", feedback_msg)

        # 3. Move to Next Question
        self.question_index += 1
        self.display_question() 

    def show_results(self):
        """Displays the final score and an option to retake or exit."""
        # Clear previous content
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        final_score = self.score
        total_questions = len(self.current_questions)
        
        ttk.Label(self.quiz_frame, text="Quiz Complete!", font=('Arial', 20, 'bold')).pack(pady=20)
        ttk.Label(self.quiz_frame, text=f"Your Final Score: {final_score} out of {total_questions}", 
                  font=('Arial', 16), foreground='green').pack(pady=10)
        
        ttk.Button(self.quiz_frame, text="Take Another Quiz", command=self.reset_and_return_to_selection).pack(pady=20)
        ttk.Button(self.quiz_frame, text="Exit Application", command=self.on_close).pack(pady=10)

    def reset_and_return_to_selection(self):
        """Resets the quiz state and shows the welcome screen."""
        self.quiz_frame.pack_forget()
        self.welcome_frame.pack(fill='both', expand=True)
        self.question_index = 0
        self.score = 0





