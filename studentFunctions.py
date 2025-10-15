# StudentFunctions.py

import tkinter as tk
from tkinter import ttk, messagebox
import random
class StudentFunctions(tk.Toplevel):
    """
    A Toplevel window for the student quiz-taking interface.
    Handles course selection, question display, answer submission, and scoring.
    """
    def __init__(self, master, db_manager, on_close_callback):
        super().__init__(master)
        self.title("Student - Take Quiz")
        self.geometry("800x600")
        self.db_manager = db_manager
        
        # Store the callback method provided by the main application
        self.on_close_callback = on_close_callback 
        # Crucial: Ensures clicking the 'X' button calls our custom close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close) 

        # NOTE: Assumes db_manager.get_all_table_names() returns a list of course names/table names
        self.course_names = self.db_manager.get_all_table_names()
        
        self.current_questions = []
        self.question_index = 0
        self.score = 0
        self.selected_answer = tk.StringVar() 
        
        self.create_selection_frame()

    def create_selection_frame(self):
        """Creates the initial screen for selecting a course/quiz."""
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill='both')

        ttk.Label(main_frame, text="Select a Course to Start the Quiz:", font=('Arial', 18, 'bold')).pack(pady=20)
        
        self.course_var = tk.StringVar(self)
        if self.course_names:
            self.course_var.set(self.course_names[0])
        else:
            ttk.Label(main_frame, text="No quizzes available.", fg='red').pack()
            ttk.Button(main_frame, text="Back to Main Menu", command=self.on_close).pack(pady=15)
            return

        course_combobox = ttk.Combobox(main_frame, textvariable=self.course_var, 
                                       values=self.course_names, state="readonly", width=40)
        course_combobox.pack(pady=10)
        
        ttk.Button(main_frame, text="Start Quiz", command=self.start_quiz, width=20).pack(pady=15)
        ttk.Button(main_frame, text="Back to Main Menu", command=self.on_close, width=20).pack(pady=10)

    def start_quiz(self):
        """Fetches questions, shuffles them, and starts the quiz interface."""
        course = self.course_var.get()
        if not course:
            messagebox.showerror("Error", "Please select a course.")
            return

        all_questions = self.db_manager.get_all_questions(course)
        
        if not all_questions:
            messagebox.showinfo("Quiz", f"No questions found for {course}.")
            self.create_selection_frame() 
            return

        random.shuffle(all_questions)
        self.current_questions = all_questions[:10]
        
        self.question_index = 0
        self.score = 0
        
        self.create_quiz_frame()
        self.display_question()
        
    def create_quiz_frame(self):
        """Sets up the GUI layout for the quiz itself."""
        for widget in self.winfo_children():
            widget.destroy()
            
        self.quiz_frame = ttk.Frame(self, padding="20")
        self.quiz_frame.pack(expand=True, fill='both')
        
        self.question_display_frame = ttk.Frame(self.quiz_frame)
        self.question_display_frame.pack(pady=10, fill='x')

        btn_frame = ttk.Frame(self.quiz_frame)
        btn_frame.pack(pady=20, fill='x')
        
        ttk.Button(btn_frame, text="Submit Answer", command=self.check_answer).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Quit Quiz (Back to Main)", command=self.on_close).pack(side=tk.RIGHT, padx=10) 
        
    def display_question(self):
        """Renders the current question and its options."""
        
        for widget in self.question_display_frame.winfo_children():
            widget.destroy()
            
        current_q = self.current_questions[self.question_index]
        
        # --- Question Display ---
        q_label = ttk.Label(self.question_display_frame, 
                            text=f"Question {self.question_index + 1}/{len(self.current_questions)}:\n\n{current_q['question_text']}",
                            font=('Arial', 14), 
                            wraplength=700, 
                            justify=tk.LEFT)
        q_label.pack(pady=20, anchor='w')

        # --- Options (Fixed to display all choices) ---
        options_data = [
            current_q['option_A'],
            current_q['option_B'],
            current_q['option_C'],
            current_q['option_D'],
        ]
        
        # Shuffle options for variety
        random.shuffle(options_data) 
        
        self.selected_answer.set("") # Clear previous selection

        option_labels = ['A', 'B', 'C', 'D'] 
        
        for i, option_text in enumerate(options_data):
            # The value stored in the StringVar will be the option's text
            option_value = option_text.strip() 
            
            # The text displayed on the radio button is "A) Option Text"
            display_text = f"{option_labels[i]}) {option_text}"
            
            rb = ttk.Radiobutton(self.question_display_frame, 
                                 text=display_text, 
                                 variable=self.selected_answer, 
                                 value=option_value)
            rb.pack(pady=5, anchor='w')

    def check_answer(self):
        """Checks the student's selected answer against the correct answer."""
        selected = self.selected_answer.get().strip()
        current_q = self.current_questions[self.question_index]
        
        if not selected:
            messagebox.showwarning("Warning", "Please select an answer before submitting.")
            return

        # Correct answer is stored as "A) Option Text". We extract the text part for comparison.
        correct_answer_db_format = current_q['correct_answer'].strip()
        correct_answer_text_only = correct_answer_db_format[3:].strip() # [3:] removes the 'A) ' or 'B) ' prefix
        
        is_correct = selected == correct_answer_text_only

        if is_correct:
            self.score += 1
            messagebox.showinfo("Result", "Correct!")
        else:
            messagebox.showinfo("Result", f"Incorrect. The correct answer was: {current_q['correct_answer']}")
            
        self.question_index += 1
        self.next_question()

    def next_question(self):
        """Determines if there are more questions or if the quiz is over."""
        if self.question_index < len(self.current_questions):
            self.display_question()
        else:
            self.show_results()
            
    def show_results(self):
        """Displays the final score and offers navigation. (STRUCTURED FOR ERROR RESISTANCE)"""
        for widget in self.winfo_children():
            widget.destroy()
            
        result_frame = ttk.Frame(self, padding="20")
        result_frame.pack(expand=True, fill='both')
        final_score_text = f"Quiz Finished!\n\nYour Score: {self.score} out of {len(self.current_questions)}"
        
        # --- ERROR-RESISTANT STRUCTURE (eliminates line break risk) ---
        score_label = ttk.Label(
            result_frame,
            text=final_score_text,
            font= ("Arial", 24, "bold")
            ) 

        # -----------------------------------------------------------------
        
        ttk.Button(result_frame, text="Take Another Quiz", command=self.create_selection_frame).pack(pady=10)
        ttk.Button(result_frame, text="Back to Main Menu", command=self.on_close).pack(pady=10)

    def on_close(self):
        """Handles closing the Toplevel window and calling the main app callback."""
        self.destroy() 
        self.on_close_callback()