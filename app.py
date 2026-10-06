
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import bcrypt
import re


app = Flask(__name__)

# Secret key used by Flask sessions
app.secret_key = "PASTE_YOUR_GENERATED_KEY_HERE"


# -----------------------------------------
# Database connection
# -----------------------------------------

def get_db_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection


# -----------------------------------------
# Input validation functions
# -----------------------------------------

def validate_username(username):

    if not 3 <= len(username) <= 20:
        return False

    return re.fullmatch(
        r"[A-Za-z0-9_]+",
        username
    ) is not None


def validate_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.fullmatch(
        pattern,
        email
    ) is not None


def validate_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[^A-Za-z0-9]", password):
        return False

    return True


# -----------------------------------------
# Home page
# -----------------------------------------

@app.route("/")
def home():

    return render_template("home.html")


# -----------------------------------------
# Registration
# -----------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Check required fields
        if not username or not email or not password:

            return "All fields are required."

        # Validate username
        if not validate_username(username):

            return (
                "Invalid username. Use 3-20 characters "
                "containing only letters, numbers, and underscore."
            )

        # Validate email
        if not validate_email(email):

            return "Please enter a valid email address."

        # Validate password
        if not validate_password(password):

            return (
                "Password must contain at least 8 characters, "
                "one uppercase letter, one lowercase letter, "
                "one number, and one special character."
            )

        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        try:

            connection = get_db_connection()

            connection.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    hashed_password.decode("utf-8")
                )
            )

            connection.commit()
            connection.close()

            return "Registration successful!"

        except sqlite3.IntegrityError:

            return "Username or email already exists."

    return render_template("register.html")


# -----------------------------------------
# Login
# -----------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Check required fields
        if not username or not password:

            return "Username and password are required."

        connection = get_db_connection()

        # Parameterized query prevents SQL injection
        user = connection.execute(
            """
            SELECT * FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        # Use the same message whether the user exists or not
        if user is None:

            return "Invalid username or password."

        # Verify password using bcrypt
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if password_matches:

            # Create session
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(
                url_for("dashboard")
            )

        return "Invalid username or password."

    return render_template("login.html")


# -----------------------------------------
# Dashboard
# -----------------------------------------

@app.route("/dashboard")
def dashboard():

    # Only logged-in users can access dashboard
    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# -----------------------------------------
# Logout
# -----------------------------------------

@app.route("/logout")
def logout():

    # Clear the current session
    session.clear()

    return redirect(
        url_for("login")
    )


# -----------------------------------------
# Run the application
# -----------------------------------------

if __name__ == "__main__":

    app.run(debug=False)