import sqlite3


# -----------------------------------------
# Create database and users table
# -----------------------------------------

def create_database():

    connection = sqlite3.connect("database.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("Database and users table created successfully!")


# -----------------------------------------
# Run database creation
# -----------------------------------------

if __name__ == "__main__":
    create_database()