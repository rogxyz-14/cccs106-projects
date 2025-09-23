import os
import sqlite3

def init_db():
    """Initializes the database and creates the contacts table if it doesn't exist."""

    # Get the parent folder path (one level up from contact_book_app)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "contacts.db")

    # Connect to the database in the parent folder
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # Create the table if it doesn’t exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    return conn


def add_contact_db(conn, name, phone, email):
    """Adds a new contact to the database, prevents duplicates."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE name=? OR phone=? OR email=?", (name, phone, email))
    if cursor.fetchone():
        raise ValueError("Contact already exists")

    cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()


def get_all_contacts_db(conn, search_term=""):
    """Retrieves all contacts from the database, supports search."""
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT id, name, phone, email FROM contacts WHERE name LIKE ?", (f"%{search_term}%",))
    else:
        cursor.execute("SELECT id, name, phone, email FROM contacts")
    return cursor.fetchall()


def update_contact_db(conn, contact_id, name, phone, email):
    """Updates an existing contact in the database."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
        (name, phone, email, contact_id)
    )
    conn.commit()


def delete_contact_db(conn, contact_id):
    """Deletes a contact from the database."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()