import tkinter as tk
from tkinter import ttk, messagebox
from databaseSetup import get_connection, COURSE_TABLES, DB_DEFAULT_PATH, ensure_db_ready

# ---------- Bootstrap DB ----------
ensure_db_ready()

# ---------- Database helpers ----------
def refresh_table(course_label):
    """Reload the question list for the selected course."""
    table = COURSE_TABLES[course_label]
    with get_connection(DB_DEFAULT_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT id, question_text, option_A, option_B, option_C, option_D, correct_option
            FROM {table}
            ORDER BY id;
        """)
        rows = cur.fetchall()

    tree.delete(*tree.get_children())
    for r in rows:
        tree.insert("", "end", values=r)

def add_question():
    """Insert or update a question."""
    cl = course_var.get()
    table = COURSE_TABLES[cl]
    q = q_text.get("1.0", "end").strip()
    A, B, C, D = (a_entry.get().strip(), b_entry.get().strip(), c_entry.get().strip(), d_entry.get().strip())
    corr = correct_var.get().strip().upper()

    if not q or corr not in ("A", "B", "C", "D"):
        messagebox.showerror("Input Error", "Please enter a question and choose a correct option (A–D).")
        return

    with get_connection(DB_DEFAULT_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {table} (question_text, option_A, option_B, option_C, option_D, correct_option)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_text) DO UPDATE SET
              option_A=excluded.option_A,
              option_B=excluded.option_B,
              option_C=excluded.option_C,
              option_D=excluded.option_D,
              correct_option=excluded.correct_option;
        """, (q, A, B, C, D, corr))
        conn.commit()

    refresh_table(cl)
    clear_form()
    messagebox.showinfo("Success", "Question added or updated successfully!")

def delete_question():
    """Delete the selected question."""
    cl = course_var.get()
    table = COURSE_TABLES[cl]
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a question to delete.")
        return

    qid = tree.item(selected[0], "values")[0]
    if not messagebox.askyesno("Confirm", f"Delete question ID {qid}?"):
        return

    with get_connection(DB_DEFAULT_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id=?;", (qid,))
        conn.commit()

    refresh_table(cl)
    clear_form()
    messagebox.showinfo("Deleted", f"Question ID {qid} deleted.")

def on_row_select(_event=None):
    """Fill the editor fields when selecting a row."""
    sel = tree.selection()
    if not sel:
        return
    vals = tree.item(sel[0], "values")
    id_var.set(vals[0])
    q_text.delete("1.0", "end")
    q_text.insert("1.0", vals[1])
    a_entry.delete(0, "end"); a_entry.insert(0, vals[2])
    b_entry.delete(0, "end"); b_entry.insert(0, vals[3])
    c_entry.delete(0, "end"); c_entry.insert(0, vals[4])
    d_entry.delete(0, "end"); d_entry.insert(0, vals[5])
    correct_var.set(vals[6])

def clear_form():
    """Clear the editor fields."""
    id_var.set("")
    q_text.delete("1.0", "end")
    for e in (a_entry, b_entry, c_entry, d_entry):
        e.delete(0, "end")
    correct_var.set("")

def on_course_change(_event=None):
    clear_form()
    refresh_table(course_var.get())

# ---------- GUI ----------
root = tk.Tk()
root.title("Admin Panel - Manage Quiz Questions")
root.geometry("1000x650")
root.configure(bg="#F9F9F9")

# Course selection bar
top = tk.Frame(root, bg="#F9F9F9")
top.pack(fill="x", padx=15, pady=10)

tk.Label(top, text="Select Course:", font=("Arial", 11), bg="#F9F9F9").pack(side="left", padx=(0,5))
course_var = tk.StringVar(value=list(COURSE_TABLES.keys())[0])
course_cb = ttk.Combobox(top, textvariable=course_var, values=list(COURSE_TABLES.keys()), state="readonly", width=40)
course_cb.pack(side="left", padx=(0,10))
course_cb.bind("<<ComboboxSelected>>", on_course_change)

# Question table
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=15, pady=5)

cols = ("ID", "Question", "A", "B", "C", "D", "Correct")
tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)

for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=120 if c != "Question" else 450, anchor="w")

tree.bind("<<TreeviewSelect>>", on_row_select)
tree.pack(fill="both", expand=True)

# Form editor
form = tk.LabelFrame(root, text="Question Editor", padx=10, pady=10, bg="#F9F9F9")
form.pack(fill="x", padx=15, pady=10)

id_var = tk.StringVar()
correct_var = tk.StringVar()

tk.Label(form, text="ID:", bg="#F9F9F9").grid(row=0, column=0, sticky="e", padx=5)
tk.Entry(form, textvariable=id_var, state="readonly", width=8).grid(row=0, column=1, padx=5, sticky="w")

tk.Label(form, text="Correct (A–D):", bg="#F9F9F9").grid(row=0, column=2, sticky="e", padx=5)
tk.Entry(form, textvariable=correct_var, width=8).grid(row=0, column=3, padx=5, sticky="w")

tk.Label(form, text="Question:", bg="#F9F9F9").grid(row=1, column=0, sticky="ne", padx=5, pady=(10,0))
q_text = tk.Text(form, width=100, height=4, wrap="word")
q_text.grid(row=1, column=1, columnspan=3, padx=5, pady=(10,0), sticky="w")

tk.Label(form, text="A:", bg="#F9F9F9").grid(row=2, column=0, sticky="e", padx=5)
a_entry = tk.Entry(form, width=90)
a_entry.grid(row=2, column=1, columnspan=3, sticky="w", pady=2)

tk.Label(form, text="B:", bg="#F9F9F9").grid(row=3, column=0, sticky="e", padx=5)
b_entry = tk.Entry(form, width=90)
b_entry.grid(row=3, column=1, columnspan=3, sticky="w", pady=2)

tk.Label(form, text="C:", bg="#F9F9F9").grid(row=4, column=0, sticky="e", padx=5)
c_entry = tk.Entry(form, width=90)
c_entry.grid(row=4, column=1, columnspan=3, sticky="w", pady=2)

tk.Label(form, text="D:", bg="#F9F9F9").grid(row=5, column=0, sticky="e", padx=5)
d_entry = tk.Entry(form, width=90)
d_entry.grid(row=5, column=1, columnspan=3, sticky="w", pady=2)

# Buttons
btn_frame = tk.Frame(root, bg="#F9F9F9")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add / Upsert", width=14, command=add_question).grid(row=0, column=0, padx=8)
tk.Button(btn_frame, text="Delete Selected", width=14, command=delete_question).grid(row=0, column=1, padx=8)
tk.Button(btn_frame, text="Clear Form", width=12, command=clear_form).grid(row=0, column=2, padx=8)

# Load first course
on_course_change()

root.mainloop()
