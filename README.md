# QA2-Submission

# 📚 Quiz Question Admin Panel

This application provides a **Graphical User Interface (GUI)** for administrators to easily manage, add, update, and delete quiz questions stored in the application's database. It is built using Python's `tkinter` library.

---

## 💻 Basic Functions

The Admin Panel simplifies question management for different courses via an interactive window.

### 1. Course Selection and Viewing

* **Select Course:** Use the **"Select Course:"** dropdown menu at the top to choose which course's questions you wish to view and manage.
* **Question Table:** Once a course is selected, the main area displays a table listing all existing questions for that course. This table shows the **ID**, **Question** text, all four **Option** texts (A, B, C, D), and the **Correct Option** (A–D).
    * *Function in Code:* The `on_course_change()` function handles updating the table when a new course is selected, which internally calls `refresh_table()`.

### 2. Editing Existing Questions

* **Select Row to Edit:** **Click on any row** in the question table. This action automatically populates the **Question Editor** form below with the selected question's data.
    * *Function in Code:* The `on_row_select()` function captures the row's data and fills the corresponding input fields.

### 3. Adding or Updating Questions

* **"Add / Upsert" Button:** This button is used for both adding *new* questions and updating *existing* ones.
    * **To Add a New Question:** Clear the form using the "Clear Form" button, enter the question text, options A-D, and the correct option letter (A, B, C, or D). Click **"Add / Upsert"**.
    * **To Update an Existing Question:** Select the question from the table (which fills the form), make your necessary changes (e.g., correct a typo or change the correct answer), and click **"Add / Upsert"**.
        * *Function in Code:* The `add_question()` function handles the database logic. It uses **`ON CONFLICT`** logic to either insert a new question or update an existing one based on the question text.

### 4. Deleting Questions

* **"Delete Selected" Button:** To remove a question, first **select the question** in the table by clicking its row, and then click the **"Delete Selected"** button.
    * A confirmation box will appear to prevent accidental deletion.
    * *Function in Code:* The `delete_question()` function handles the selection and database removal based on the question's ID.

### 5. Clearing the Form

* **"Clear Form" Button:** This button instantly clears all text from the **Question Editor** fields, making it easy to start entering a brand-new question without old data.
    * *Function in Code:* The `clear_form()` function resets the input variables and text areas.

---

## 🛠️ Key Technical Components

* **Database Interaction:** The functions rely on `get_connection()` to establish a connection to the SQLite database (`DB_DEFAULT_PATH`).
* **GUI Library:** The user interface is built using `tkinter` and the `ttk` (Themed Tkinter) module for modern widgets like the `Combobox` and `Treeview`.
* **Error Handling:** Basic input validation checks (e.g., ensuring a question is entered and a correct option is chosen) and confirmation messages are used via `messagebox`.


# 📝 Quiz Student Tab

This application is the **Student Tab** for the quiz system, providing a user interface where students can select a course, navigate through questions, select answers, check instant feedback, and submit their quiz for a final score. It is built using Python's `tkinter` library.

---

## 🚀 Basic Functions (Student Workflow)




The Student Tab guides the user through the process of taking a quiz.

### 1. Course Selection

* **Initial Setup:** When the script starts, it first checks if a course name was passed as a command-line argument.
* **Course Picker:** If no course is specified, a small window appears allowing the user to **"Choose Course"** from a list of available courses in the database.
    * *Function in Code:* The `pick_course_if_needed()` function handles the GUI for course selection.
* **Load Questions:** Once a course is selected, the application loads the questions for that course, shuffling them for a fresh experience.
    * *Function in Code:* `load_questions_or_die()` fetches the questions using `fetch_questions()`.

***

### 2. Navigating the Quiz

* **Display:** The main window shows the current question number (e.g., "Q1/10"), the question text, and the four multiple-choice options (A, B, C, D).
    * *Function in Code:* `render_question(i)` updates the GUI elements to display the question at the current index (`i`).
* **Movement Controls:**
    * **"◀ Back"** Button: Moves to the previous question. Disabled on the first question.
    * **"Next ▶"** Button: Moves to the next question. Disabled on the last question.
    * *Function in Code:* The `move(delta)` function handles changing the question index.

***

### 3. Answering Questions

* **Selecting an Option:** Students select their answer by clicking the **radio button** next to the option (A, B, C, or D).
    * *Function in Code:* The `on_choice()` function immediately records the selected answer for the current question ID in the `user_answers` state dictionary. This ensures answers are saved as the student navigates.

***

### 4. Instant Feedback

* **"Check" Button:** Students can click this button at any time to receive instant feedback on the **current question**.
    * A pop-up message will indicate if the answer is **Correct** (✅) or **Incorrect** (❌) and will show the correct option.
    * If an **explanation** for the answer exists in the database, it will also be displayed in the pop-up.
    * *Function in Code:* The `check_current()` function retrieves the user's answer and the correct answer, comparing them and displaying the appropriate feedback box.

***

### 5. Submitting and Scoring

* **"Submit Quiz" Button:** When the student is ready, they click this button to end the quiz.
    * A warning will appear if not all questions have been answered, giving the student a chance to return to the quiz.
* **Final Score:** After submission, a final pop-up displays the course name and the student's **total score** (e.g., "Score: 8/10").
    * *Function in Code:* The `submit_quiz()` function uses the `grade_quiz()` helper to calculate the score based on the collected `user_answers` and the complete `questions` list.


    # 🚪 Main Application Entry (Login Selector)

This script (`app_entry.py` or similar) serves as the **main gateway** to the entire quiz application. It is a lightweight GUI built with `tkinter` that allows users to select their role: **Admin** or **Student**.

---

## 🔑 Basic Functions

### 1. Initial Setup and Database Check

* **Database Bootstrap:** The application's first step is to call `ensure_db_ready()`. This ensures the necessary database files and default tables are created before any user interaction begins.
    * If this step fails, the user receives a critical error message, and the application raises an exception.

### 2. Role Selection

The main screen presents two options for logging in:

| Role | Access Method | Function |
| :--- | :--- | :--- |
| **Admin** | Password Entry | Manages the application's questions and content. |
| **Student** | Direct Access | Takes quizzes for available courses. |

### 3. Admin Login

* **Authentication:** The user is prompted to enter a password.
* **Access:** If the entered password matches the hardcoded `ADMIN_PASSWORD` ("admin"), the application launches the **Admin Panel** (`adminApp.py`) in a new, separate process.
* **Failure:** If the password is incorrect, an "Access denied" error message is displayed.
    * *Function in Code:* `on_admin_login()` handles this logic and calls `launch("adminApp.py")`.

### 4. Student Course Selection

* **Course Picker View:** Clicking **"Student → Choose Course"** transitions the main window to a new view, replacing the login fields with a list of available courses.
* **List Courses:** The application dynamically queries the database to display a button for every available course.
* **Launch Quiz:** Clicking any of the course buttons launches the **Student Quiz Tab** (`student_quiz.py`) in a new process, passing the selected course name as an argument.
    * *Function in Code:* `show_student_courses()` handles loading the course names and creating the dynamic buttons, which then call `launch("student_quiz.py", name)`.
* **Navigation:** A **"⬅ Back"** button is provided to return to the initial Login screen.

---

## 🛠️ Key Technical Components

* **Process Management:** The central `launch()` function is responsible for opening the Admin and Student apps. It uses **`subprocess.Popen`** to run these Python scripts independently, ensuring the main login window doesn't wait for them to close.
* **Dynamic UI:** The `render_login_screen()` and `show_student_courses()` functions dynamically destroy and rebuild the main window's contents to switch between the login view and the course selection view.




# 💾 Database Setup and Helpers

The `databaseSetup.py` script manages the SQLite database (`ljdialQuizDB.db`) that stores all the quiz questions for the application. It handles creation, population (seeding), and provides helper functions for the Admin and Student tabs to interact with the data efficiently.

---

## ⚙️ Core Setup and Constants

* **Database File:** All data is stored in **`ljdialQuizDB.db`** (defined by `DB_DEFAULT_PATH`).
* **Course Mapping:** The **`COURSE_TABLES`** dictionary defines the relationship between human-readable course names (like "Business Applications") and their corresponding database table names (like "Business\_Applications").
    * This ensures that the application can manage multiple quizzes within a single database file.

### `get_connection()`
This function establishes a connection to the SQLite database. It applies recommended settings (**PRAGMAs**) like `journal_mode = WAL` and `synchronous = NORMAL` to improve concurrent access and performance, which is important when both the Admin and Student tabs might be running.

### `_TABLE_SCHEMA`
This SQL template is used to create the tables. Each course table has the following columns:
* `id`: Primary key for unique identification.
* `question_text`: The main question (set as **UNIQUE** to prevent duplicate questions).
* `option_A` through `option_D`: The four multiple-choice options.
* `correct_option`: The letter ('A', 'B', 'C', or 'D') of the correct answer.
* `explanation`: Optional text providing context/reasoning for the answer.

---

## 🏗️ Database Initialization and Seeding

### `create_and_populate_db()`
This is the core function for setting up the database.
1.  **Creates Tables:** It ensures a table exists for every course defined in `COURSE_TABLES`.
2.  **Seeds Data:** It inserts the initial set of quiz questions, defined in the private function `_seed_data()`, into their respective tables.
    * The **`ON CONFLICT(question_text) DO UPDATE`** clause ensures the function is **idempotent**—you can run it multiple times, and it will safely insert new questions or update existing ones (based on matching `question_text`) without duplicating entries.

### `ensure_db_ready()`
This function acts as a safety check at application startup.
* It checks the current question count for all tables.
* If any table is empty (or if the database file is missing/corrupted), it automatically calls `create_and_populate_db()` to create and seed the tables, guaranteeing the app has data to run.

---

## 🤝 Application Helper Functions

These functions are used by the Admin and Student application scripts to retrieve and process data.

### `list_courses()`
* **Purpose:** Returns a simple list of human-readable course names (e.g., `["Business Applications", "Business Management"]`).
* **Used by:** The **Main Entry App** and **Student Tab** to populate the course selection menus.

### `count_questions()`
* **Purpose:** Returns a dictionary showing the number of questions currently in each course table.
* **Used by:** The `ensure_db_ready()` check.

### `fetch_questions()`
* **Purpose:** Retrieves all questions for a given `course_label` and formats the data into a clean **List of Dictionaries** suitable for the GUI.
* **Key Features:**
    * Allows **shuffling** (`shuffle=True` by default) for a new quiz order every time.
    * Allows limiting the number of questions (`limit=N`).
* **Used by:** The **Student Tab** to load a quiz.

### `grade_quiz()`
* **Purpose:** Calculates the student's score.
* **Logic:** Compares the student's submitted answers (`user_answers`) against the correct answers stored in the `questions` list and returns the total number of correct answers.
* **Used by:** The **Student Tab** upon quiz submission.