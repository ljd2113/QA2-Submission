import sqlite3
import random
from typing import Dict, List, Tuple, Optional

# ===== Public constants =====
DB_DEFAULT_PATH = "ljdialQuizDB.db"

COURSE_TABLES: Dict[str, str] = {
    "Business Applications": "Business_Applications",
    "Business Management": "Business_Management",
    "Business Analytics": "Business_Analytics",
    "Business Database Management": "Business_Database_Management",
}

# ===== Connection helper =====
def get_connection(db_path: str = DB_DEFAULT_PATH) -> sqlite3.Connection:
    """
    Return a sqlite3 connection with sane pragmas enabled.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    # Good defaults for desktop apps
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

# ===== Schema + Populate (idempotent) =====
_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    option_A TEXT NOT NULL,
    option_B TEXT NOT NULL,
    option_C TEXT NOT NULL,
    option_D TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK (correct_option IN ('A','B','C','D')),
    explanation TEXT DEFAULT NULL,
    UNIQUE(question_text)
);
"""

def _create_tables(cur: sqlite3.Cursor) -> None:
    for t in COURSE_TABLES.values():
        cur.execute(_TABLE_SCHEMA.format(table_name=t))

def _normalize_block(
    rows: List[Tuple[str, str, str, str, str, str]]
) -> List[Tuple[str, str, str, str, str, str, Optional[str]]]:
    """
    Input rows:  (q, 'A) ...', 'B) ...', 'C) ...', 'D) ...', 'X) correct text')
    Output rows: (q, A, B, C, D, correct_letter, explanation_text)
    """
    out: List[Tuple[str, str, str, str, str, str, Optional[str]]] = []
    for (q, A, B, C, D, correct_full) in rows:
        def strip_label(s: str) -> str:
            return s.split(") ", 1)[1] if ") " in s else s
        letter = correct_full.split(")")[0].strip()
        letter = letter if letter in ("A", "B", "C", "D") else "A"
        expl = correct_full.split(")", 1)[1].strip() if ")" in correct_full else None
        out.append((q, strip_label(A), strip_label(B), strip_label(C), strip_label(D), letter, expl))
    return out

def create_and_populate_db(db_path: str = DB_DEFAULT_PATH) -> None:
    """
    Create tables if missing and upsert seed questions.
    Safe to re-run (UNIQUE(question_text) + ON CONFLICT UPDATE).
    """
    data_blocks = _seed_data()

    with get_connection(db_path) as conn:
        cur = conn.cursor()
        _create_tables(cur)

        insert_sql = """
        INSERT INTO {table_name}
        (question_text, option_A, option_B, option_C, option_D, correct_option, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(question_text) DO UPDATE SET
            option_A=excluded.option_A,
            option_B=excluded.option_B,
            option_C=excluded.option_C,
            option_D=excluded.option_D,
            correct_option=excluded.correct_option,
            explanation=excluded.explanation;
        """

        for table_name, rows_raw in data_blocks.items():
            rows = _normalize_block(rows_raw)
            cur.executemany(insert_sql.format(table_name=table_name), rows)

        conn.commit()

def ensure_db_ready(db_path: str = DB_DEFAULT_PATH) -> None:
    """
    Quick guard: if missing/empty, (re)create & seed.
    Call this once at app start.
    """
    try:
        counts = count_questions(db_path)
        if any(v == 0 for v in counts.values()):
            create_and_populate_db(db_path)
    except Exception:
        create_and_populate_db(db_path)

# ===== GUI-friendly helpers (optional but useful) =====
def list_courses() -> List[str]:
    return list(COURSE_TABLES.keys())

def count_questions(db_path: str = DB_DEFAULT_PATH) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        for label, table in COURSE_TABLES.items():
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            counts[label] = int(cur.fetchone()[0])
    return counts

def fetch_questions(
    course_label: str,
    db_path: str = DB_DEFAULT_PATH,
    limit: Optional[int] = None,
    shuffle: bool = True
) -> List[Dict]:
    """
    Returns:
    [
      {"id": 1, "text": "...",
       "options": {"A": "...","B":"...","C":"...","D":"..."},
       "correct": "B", "explanation": "..."},
       ...
    ]
    """
    if course_label not in COURSE_TABLES:
        raise ValueError(f"Unknown course label: {course_label}")

    table = COURSE_TABLES[course_label]
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT id, question_text, option_A, option_B, option_C, option_D, correct_option, COALESCE(explanation, '')
            FROM {table};
        """)
        rows = cur.fetchall()

    questions = [
        {
            "id": r[0],
            "text": r[1],
            "options": {"A": r[2], "B": r[3], "C": r[4], "D": r[5]},
            "correct": r[6],
            "explanation": r[7],
        }
        for r in rows
    ]
    if shuffle:
        random.shuffle(questions)
    return questions[:limit] if (limit and limit > 0) else questions

def grade_quiz(user_answers: Dict[int, str], questions: List[Dict]) -> int:
    lookup = {q["id"]: q for q in questions}
    return sum(1 for qid, ans in user_answers.items()
               if qid in lookup and ans == lookup[qid]["correct"])

# ===== Seed data (your original questions) =====
def _seed_data() -> Dict[str, List[Tuple[str, str, str, str, str, str]]]:
    business_applications = [
        ("What is the output of `print(type(10/2))` in Python?", "A) <class 'int'>", "B) <class 'float'>", "C) <class 'str'>", "D) 5.0", "B) <class 'float'>"),
        ("Which keyword is used to define a function in Python?", "A) `func`", "B) `define`", "C) `def`", "D) `function`", "C) `def`"),
        ("How do you start a multi-line comment or docstring in Python?", "A) `//`", "B) `/*`", "C) `\"\"\"`", "D) `#`", "C) `\"\"\"`"),
        ("Which data structure is ordered and mutable?", "A) Tuple", "B) Set", "C) Dictionary", "D) List", "D) List"),
        ("What method adds an element to the end of a list?", "A) `.insert()`", "B) `.add()`", "C) `.append()`", "D) `.push()`", "C) `.append()`"),
        ("What is the correct way to check if `x` is greater than 5 AND less than 10?", "A) `x > 5 and x < 10`", "B) `5 < x < 10`", "C) `A and B are correct`", "D) `x > 5 & x < 10`", "C) `A and B are correct`"),
        ("In a `for` loop, what does the `range(5)` function iterate over?", "A) 1, 2, 3, 4, 5", "B) 0, 1, 2, 3, 4", "C) 0, 1, 2, 3, 4, 5", "D) 1, 2, 3, 4", "B) 0, 1, 2, 3, 4"),
        ("Which of the following is NOT a valid variable name in Python?", "A) `_my_var`", "B) `myVar2`", "C) `2myVar`", "D) `my_var`", "C) `2myVar`"),
        ("What is the primary purpose of the `if __name__ == \"__main__\":` block?", "A) To define global variables.", "B) To import external modules.", "C) To ensure code runs only when the script is executed directly.", "D) To define the main class.", "C) To ensure code runs only when the script is executed directly."),
        ("What does the `pass` statement do in Python?", "A) Jumps to the next loop iteration.", "B) Exits the loop.", "C) Does nothing; it's a placeholder.", "D) Skips the current block of code.", "C) Does nothing; it's a placeholder.")
    ]

    business_management = [
        ("Which of the following is a primary component of a good business strategy?", "A) Daily operational tasks", "B) Long-term goals and resource allocation", "C) Employee break times", "D) Server maintenance", "B) Long-term goals and resource allocation"),
        ("In management psychology, what is **Maslow's Hierarchy of Needs** often used to explain?", "A) Financial accounting principles", "B) Employee motivation", "C) Marketing segmentation", "D) IT infrastructure", "B) Employee motivation"),
        ("What leadership style involves the leader making decisions and announcing them to the group?", "A) Democratic", "B) Laissez-faire", "C) Autocratic", "D) Participative", "C) Autocratic"),
        ("**Emotional Intelligence (EQ)** in the workplace is primarily concerned with:", "A) Technical skills and coding ability", "B) The ability to perceive and manage emotions", "C) High-speed data processing", "D) Strict adherence to rules", "B) The ability to perceive and manage emotions"),
        ("What is the term for breaking down a large project into smaller, manageable tasks?", "A) Micromanagement", "B) Delegation", "C) Work Breakdown Structure (WBS)", "D) Brainstorming", "C) Work Breakdown Structure (WBS)"),
        ("A **SWOT analysis** helps a business identify its:", "A) Sales, Wages, Operating, and Taxes", "B) Strengths, Weaknesses, Opportunities, and Threats", "C) Suppliers, Workers, Outsourcers, and Technologies", "D) Stock, Wealth, Overhead, and Turnover", "B) Strengths, Weaknesses, Opportunities, and Threats"),
        ("What is **Groupthink**?", "A) A highly productive team meeting.", "B) A phenomenon where the desire for conformity in a group results in irrational decision-making.", "C) A method for generating new ideas.", "D) A managerial structure.", "B) A phenomenon where the desire for conformity in a group results in irrational decision-making."),
        ("The 'P' in the **POLC framework** of management stands for:", "A) Performance", "B) Planning", "C) Procedure", "D) Production", "B) Planning"),
        ("In **Herzberg's Two-Factor Theory**, what are factors like salary and working conditions called?", "A) Motivators", "B) Hygiene Factors", "C) Achievement Factors", "D) Growth Factors", "B) Hygiene Factors"),
        ("What is the process of setting performance goals and providing feedback called?", "A) Mentorship", "B) Coaching", "C) Performance Appraisal", "D) Recruitment", "C) Performance Appraisal")
    ]

    business_analytics = [
        ("Which Excel function is best for a conditional sum (summing values that meet a criterion)?", "A) `SUM()`", "B) `AVERAGEIF()`", "C) `SUMIF()`", "D) `COUNTIF()`", "C) `SUMIF()`"),
        ("What is the primary purpose of an **Excel Pivot Table**?", "A) To perform complex arithmetic operations.", "B) To summarize, analyze, explore, and present data.", "C) To create macros for automation.", "D) To import data from external sources.", "B) To summarize, analyze, explore, and present data."),
        ("A **Line Chart** is generally the best choice for showing:", "A) Proportions of a whole.", "B) Distribution of data points.", "C) Trends over time.", "D) Correlation between two variables.", "C) Trends over time."),
        ("What kind of analysis is performed when a manager examines a sales chart to understand if a recent marketing campaign was effective?", "A) Prescriptive Analysis", "B) Diagnostic Analysis", "C) Predictive Analysis", "D) Descriptive Analysis", "D) Descriptive Analysis"),
        ("In Excel, what does the **'Relative'** reference `A1` change to when copied one cell down?", "A) `A1`", "B) `$A$1`", "C) `A2`", "D) `B1`", "C) `A2`"),
        ("To keep the **column** fixed but allow the **row** to change when copying a formula, what mixed reference should be used?", "A) `$A1`", "B) `A$1`", "C) `$A$1`", "D) `A1`", "A) `$A1`"),
        ("Which term describes the process of identifying errors or inconsistencies in data to improve its quality?", "A) Data Mining", "B) Data Cleansing (or Scrubbing)", "C) Data Modeling", "D) Data Visualization", "B) Data Cleansing (or Scrubbing)"),
        ("A **Bar Chart** is most effective for comparing:", "A) Continuous change over time.", "B) Values across different categories.", "C) Parts of a whole.", "D) The frequency of an event.", "B) Values across different categories."),
        ("In a Pivot Table, what area is used to filter the entire table's data?", "A) Values", "B) Rows", "C) Filters (or Report Filter)", "D) Columns", "C) Filters (or Report Filter)"),
        ("The goal of **Predictive Analytics** is to:", "A) Understand why an event happened.", "B) Suggest a course of action.", "C) Forecast what might happen in the future.", "D) Summarize current data.", "C) Forecast what might happen in the future.")
    ]

    business_db_mgmt = [
        ("Which Relational Algebra operation combines the tuples from two relations, eliminating duplicates?", "A) Join", "B) Project", "C) Union", "D) Select", "C) Union"),
        ("In an **Entity-Relationship (ER) Model**, a diamond shape represents a(n):", "A) Entity", "B) Attribute", "C) Relationship", "D) Primary Key", "C) Relationship"),
        ("What is the purpose of **Normalization** in a relational database?", "A) To speed up queries.", "B) To reduce data redundancy and improve data integrity.", "C) To encrypt the database.", "D) To create views.", "B) To reduce data redundancy and improve data integrity."),
        ("Which Normal Form (NF) requires that there are no partial dependencies of non-key attributes on the primary key?", "A) 1NF", "B) 2NF", "C) 3NF", "D) BCNF", "B) 2NF"),
        ("A **Foreign Key** is used to:", "A) Uniquely identify a record in a table.", "B) Establish a link between two tables.", "C) Store very large data objects.", "D) Sort the data in a table.", "B) Establish a link between two tables."),
        ("In **Relational Algebra**, the **Select** (σ) operation is used to:", "A) Choose specific columns.", "B) Filter rows based on a condition.", "C) Combine two tables.", "D) Rename a column.", "B) Filter rows based on a condition."),
        ("A **recursive relationship** in an ERD is one between:", "A) Two different entities.", "B) An entity and an attribute.", "C) Two different attributes.", "D) An entity and itself.", "D) An entity and itself."),
        ("What does the 'R' stand for in **RDBMS**?", "A) Restricted", "B) Relational", "C) Redundant", "D) Retrieval", "B) Relational"),
        ("The condition for **Third Normal Form (3NF)** is: The table must be in 2NF, and there should be no:", "A) Partial Dependencies.", "B) Multi-valued Attributes.", "C) Transitive Dependencies.", "D) Redundant Data.", "C) Transitive Dependencies."),
        ("A **many-to-many (M:N)** relationship in an ERD is typically resolved in a relational model by:", "A) Creating a supertype/subtype.", "B) Introducing a new **linking table**.", "C) Using a composite key in one of the tables.", "D) Splitting the relationship.", "B) Introducing a new **linking table**.")
    ]

    return {
        COURSE_TABLES["Business Applications"]: business_applications,
        COURSE_TABLES["Business Management"]: business_management,
        COURSE_TABLES["Business Analytics"]: business_analytics,
        COURSE_TABLES["Business Database Management"]: business_db_mgmt,
    }

# Optional: run this file directly to (re)create the DB
if __name__ == "__main__":
    create_and_populate_db()
    print("Database created and seeded at:", DB_DEFAULT_PATH)
    print("Counts:", count_questions())
