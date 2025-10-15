# my_database.db

import sqlite3
DATABASE_FILE = 'ljdialQuizDB.db'

class DBManager:
    """Manages all database connection and CRUD operations."""

    def __init__(self, db_name=DATABASE_FILE):
        self.db_name = db_name

    def connect(self):
        """Returns a connection and cursor object."""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row # Allows accessing columns by name
            return conn, conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None, None

    def get_all_table_names(self):
        """Fetches all course table names."""
        conn, cursor = self.connect()
        if not conn: return []
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_all_questions(self, table_name):
        """Fetches all questions from a specific course table."""
        conn, cursor = self.connect()
        if not conn: return []
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            # Convert rows (sqlite.Row objects) to a list of dicts for easier GUI handling
            questions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return questions
        except sqlite3.OperationalError as e:
            print(f"Error fetching questions from {table_name}: {e}")
            conn.close()
            return []

    # --- ADMIN Functions (CRUD) ---

    def add_question(self, table_name, question_data):
        """Adds a new question to the specified table."""
        conn, cursor = self.connect()
        if not conn: return False
        
        try:
            sql = f"""
            INSERT INTO {table_name} 
            (question, option_A, option_B, option_C, option_D, correct_answer) 
            VALUES (?, ?, ?, ?, ?, ?);
            """
            cursor.execute(sql, (
                question_data['question'],
                question_data['option_A'],
                question_data['option_B'],
                question_data['option_C'],
                question_data['option_D'],
                question_data['correct_answer']
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error adding question: {e}")
            conn.close()
            return False

    def delete_question(self, table_name, question_id):
        """Deletes a question by its ID."""
        conn, cursor = self.connect()
        if not conn: return False
        
        try:
            sql = f"DELETE FROM {table_name} WHERE id = ?;"
            cursor.execute(sql, (question_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting question: {e}")
            conn.close()
            return False

    def update_question(self, table_name, question_data):
        """Updates an existing question."""
        conn, cursor = self.connect()
        if not conn: return False
        
        try:
            sql = f"""
            UPDATE {table_name} SET
            question = ?, option_A = ?, option_B = ?, option_C = ?, 
            option_D = ?, correct_answer = ?
            WHERE id = ?;
            """
            cursor.execute(sql, (
                question_data['question'],
                question_data['option_A'],
                question_data['option_B'],
                question_data['option_C'],
                question_data['option_D'],
                question_data['correct_answer'],
                question_data['id']
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating question: {e}")
            conn.close()
            return False

# You would add a method here for 'Adding new courses' which is creating a new table.
# For simplicity, we assume the initial 4 tables are sufficient for the assignment.