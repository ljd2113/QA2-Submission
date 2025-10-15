import sqlite3

def create_and_populate_db(db_name="ljdialQuizDB.db"):
    """
    Creates an SQLite database file with four tables and populates them
    with multiple-choice questions.
    """
    conn = None # Initialize conn to None for the finally block
    try:
        # Connect to the database file (it will be created if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Define the structure for all tables using the CORRECTED COLUMN NAMES
        table_schema = """
CREATE TABLE IF NOT EXISTS {} (
    id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,  
    option_A TEXT NOT NULL,
    option_B TEXT NOT NULL,
    option_C TEXT NOT NULL,
    option_D TEXT NOT NULL,
    correct_option TEXT NOT NULL
);
"""
        
        # Table names
        tables = [
            "Business_Applications",
            "Business_Management",
            "Business_Analytics",
            "Business_Database_Management"
        ]

        # Create the tables
        for table_name in tables:
            # Replace spaces with underscores for SQL
            sql_table_name = table_name.replace(" ", "_")
            cursor.execute(table_schema.format(sql_table_name))
            print(f"Table '{sql_table_name}' created successfully.")

        # --- Data for the tables (10 questions each) ---

        # 1. Business Applications (Python Programming)
        business_applications_data = [
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
        
        # 2. Business Management (Components and Psychology of Working)
        business_management_data = [
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
        
        # 3. Business Analytics (Excel, Pivot Tables, Charts, Interpretation)
        business_analytics_data = [
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
        
        # 4. Business Database Management (Relational Algebra, ER Models, Normalization)
        business_db_management_data = [
            ("Which Relational Algebra operation combines the tuples from two relations, eliminating duplicates?", "A) Join", "B) Project", "C) Union", "D) Select", "C) Union"),
            ("In an **Entity-Relationship (ER) Model**, a diamond shape represents a(n):", "A) Entity", "B) Attribute", "C) Relationship", "D) Primary Key", "C) Relationship"),
            ("What is the purpose of **Normalization** in a relational database?", "A) To speed up queries.", "B) To reduce data redundancy and improve data integrity.", "C) To encrypt the database.", "D) To create views.", "B) To reduce data redundancy and improve data integrity."),
            ("Which Normal Form (NF) requires that there are no partial dependencies of non-key attributes on the primary key?", "A) 1NF", "B) 2NF", "C) 3NF", "D) BCNF", "B) 2NF"),
            ("A **Foreign Key** is used to:", "A) Uniquely identify a record in a table.", "B) Establish a link between two tables.", "C) Store very large data objects.", "D) Sort the data in a table.", "B) Establish a link between two tables."),
            ("In **Relational Algebra**, the **Select** ($\sigma$) operation is used to:", "A) Choose specific columns.", "B) Filter rows based on a condition.", "C) Combine two tables.", "D) Rename a column.", "B) Filter rows based on a condition."),
            ("A **recursive relationship** in an ERD is one between:", "A) Two different entities.", "B) An entity and an attribute.", "C) Two different attributes.", "D) An entity and itself.", "D) An entity and itself."),
            ("What does the 'R' stand for in **RDBMS**?", "A) Restricted", "B) Relational", "C) Redundant", "D) Retrieval", "B) Relational"),
            ("The condition for **Third Normal Form (3NF)** is: The table must be in 2NF, and there should be no:", "A) Partial Dependencies.", "B) Multi-valued Attributes.", "C) Transitive Dependencies.", "D) Redundant Data.", "C) Transitive Dependencies."),
            ("A **many-to-many (M:N)** relationship in an ERD is typically resolved in a relational model by:", "A) Creating a supertype/subtype.", "B) Introducing a new **linking table**.", "C) Using a composite key in one of the tables.", "D) Splitting the relationship.", "B) Introducing a new **linking table**.")
        ]

        # --- Insert Data ---

        # The correct helper function for inserting data
        def insert_data(table_name, data):
            # This SQL INSERT statement uses the CORRECTED COLUMN NAMES
            sql_insert = f"""
            INSERT INTO {table_name} 
            (question_text, option_A, option_B, option_C, option_D, correct_option) 
            VALUES (?, ?, ?, ?, ?, ?);
            """
            cursor.executemany(sql_insert, data)
            print(f"Inserted {len(data)} questions into '{table_name}'.")

        # Execute data insertion
        insert_data("Business_Applications", business_applications_data)
        insert_data("Business_Management", business_management_data)
        insert_data("Business_Analytics", business_analytics_data)
        insert_data("Business_Database_Management", business_db_management_data)

        # Commit the changes and close the connection
        conn.commit()
        print("\nDatabase creation and population complete! 🥳")
        print(f"File '{db_name}' has been successfully created.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# This is the standard execution block and must be at the very bottom
if __name__ == "__main__":
    create_and_populate_db()