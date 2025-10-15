import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
from databaseSetup import fetch_questions, grade_quiz, list_courses, ensure_db_ready

# ---------- Helpers ----------
def pick_course_if_needed() -> str:
    """If no course provided, let user pick one."""
    courses = list_courses()
    if not courses:
        messagebox.showerror("No courses", "No courses found in the database.")
        sys.exit(1)

    sel = {"value": None}

    def confirm():
        val = combo.get().strip()
        if not val:
            messagebox.showwarning("Pick one", "Please select a course.")
            return
        sel["value"] = val
        picker.destroy()

    picker = tk.Tk()
    picker.title("Choose Course")
    picker.geometry("350x140")
    picker.configure(bg="#F8F8F8")

    tk.Label(picker, text="Select a course", font=("Arial", 12, "bold"), bg="#F8F8F8").pack(pady=10)
    combo = ttk.Combobox(picker, values=courses, state="readonly", width=30)
    combo.pack()
    combo.current(0)
    tk.Button(picker, text="Start Quiz", width=14, command=confirm).pack(pady=12)

    picker.mainloop()
    if not sel["value"]:
        sys.exit(0)
    return sel["value"]

def load_questions_or_die(course_name: str) -> List[Dict]:
    try:
        qs = fetch_questions(course_name, shuffle=True)
    except Exception as e:
        messagebox.showerror("Load error", f"Failed to load questions for {course_name}.\n\n{e}")
        sys.exit(1)
    if not qs:
        messagebox.showerror("No questions", f"No questions found for {course_name}.")
        sys.exit(1)
    return qs

# ---------- Ensure DB ready ----------
ensure_db_ready()

# ---------- Course selection ----------
COURSE = sys.argv[1] if len(sys.argv) >= 2 else pick_course_if_needed()
questions = load_questions_or_die(COURSE)

# ---------- State ----------
user_answers: Dict[int, str] = {}
idx = 0

# ---------- Functions ----------
def render_question(i: int) -> None:
    q = questions[i]
    q_text.set(f"Q{i+1}/{len(questions)}: {q['text']}")
    choice_var.set(user_answers.get(q["id"], ""))
    for letter in ("A", "B", "C", "D"):
        opt_labels[letter].config(text=f"{letter}) {q['options'][letter]}")
    back_btn.config(state=("normal" if i > 0 else "disabled"))
    next_btn.config(state=("normal" if i < len(questions) - 1 else "disabled"))

def on_choice() -> None:
    qid = questions[idx]["id"]
    user_answers[qid] = choice_var.get()

def move(delta: int) -> None:
    global idx
    new_i = idx + delta
    if 0 <= new_i < len(questions):
        idx = new_i
        render_question(idx)

def check_current() -> None:
    q = questions[idx]
    ans = user_answers.get(q["id"])
    if not ans:
        messagebox.showwarning("No answer", "Please select an option.")
        return
    msg = "✅ Correct!" if ans == q["correct"] else f"❌ Incorrect. Correct: {q['correct']}"
    if q["explanation"]:
        msg += f"\n\n{q['explanation']}"
    messagebox.showinfo("Feedback", msg)

def submit_quiz() -> None:
    if len(user_answers) < len(questions):
        if not messagebox.askyesno("Unanswered", "Some questions are unanswered. Submit anyway?"):
            return
    score = grade_quiz(user_answers, questions)
    messagebox.showinfo("Final Score", f"{COURSE}\n\nScore: {score}/{len(questions)}")

# ---------- GUI Layout ----------
root = tk.Tk()
root.title(f"{COURSE} Quiz")
root.geometry("720x520")
root.configure(bg="#F9F9F9")

frame = tk.Frame(root, bg="#F9F9F9")
frame.pack(expand=True, fill="both", padx=25, pady=20)

q_text = tk.StringVar()
choice_var = tk.StringVar()

# Question Text
tk.Label(
    frame, textvariable=q_text, wraplength=650, justify="left",
    font=("Arial", 13, "bold"), bg="#F9F9F9"
).pack(anchor="w", pady=(10, 15))

# Choice buttons (grouped horizontally)
options_frame = tk.Frame(frame, bg="#F9F9F9")
options_frame.pack(anchor="w", padx=20)

opt_labels = {}
for letter in ("A", "B", "C", "D"):
    opt_row = tk.Frame(options_frame, bg="#F9F9F9")
    opt_row.pack(anchor="w", pady=4)
    tk.Radiobutton(opt_row, variable=choice_var, value=letter, bg="#F9F9F9",
                   activebackground="#F9F9F9", command=on_choice).pack(side="left", padx=(0, 5))
    lbl = tk.Label(opt_row, text="", font=("Arial", 12), bg="#F9F9F9", wraplength=600, justify="left")
    lbl.pack(side="left")
    opt_labels[letter] = lbl

# Buttons (Centered)
controls = tk.Frame(frame, bg="#F9F9F9")
controls.pack(pady=20)

back_btn = tk.Button(controls, text="◀ Back", width=10, command=lambda: move(-1))
check_btn = tk.Button(controls, text="Check", width=10, command=check_current)
next_btn = tk.Button(controls, text="Next ▶", width=10, command=lambda: move(1))
back_btn.grid(row=0, column=0, padx=6)
check_btn.grid(row=0, column=1, padx=6)
next_btn.grid(row=0, column=2, padx=6)

tk.Button(frame, text="Submit Quiz", width=12, command=submit_quiz).pack(pady=6)

# Start with first question
render_question(idx)

root.mainloop()
