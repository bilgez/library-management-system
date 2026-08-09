"""
init_db.py — creates library.db (SQLite) with schema, triggers, and seed data.

This mirrors the original SQL Server design (Books / Students / Borrowing / Librarians
tables + AFTER INSERT / AFTER UPDATE triggers on Borrowing that keep Copies_Available in
sync) and folds the original MongoDB "book_reviews" collection into a simple Reviews table
for this lightweight demo version.

Run this once before starting the app:
    python init_db.py
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

SCHEMA = """
CREATE TABLE Books (
    Book_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    Genre TEXT,
    ISBN TEXT,
    Copies_Available INTEGER NOT NULL DEFAULT 0,
    Metadata TEXT  -- JSON string: publisher, edition, year, pages, language, summary...
);

CREATE TABLE Students (
    Student_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT,
    Major TEXT
);

CREATE TABLE Borrowing (
    Borrow_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Book_ID INTEGER REFERENCES Books(Book_ID),
    Student_ID INTEGER REFERENCES Students(Student_ID),
    Borrow_Date TEXT NOT NULL,
    Due_Date TEXT NOT NULL,
    Return_Date TEXT,
    Status TEXT NOT NULL DEFAULT 'Borrowed'  -- 'Borrowed' | 'Returned'
);

-- Stands in for the original MongoDB "book_reviews" collection
CREATE TABLE Reviews (
    Review_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Book_ID INTEGER REFERENCES Books(Book_ID),
    Student_ID INTEGER REFERENCES Students(Student_ID),
    Rating INTEGER CHECK (Rating BETWEEN 1 AND 5),
    Comment TEXT,
    Created_At TEXT DEFAULT (datetime('now'))
);

-- ===== Triggers: same behaviour as the original SQL Server triggers =====

CREATE TRIGGER trg_DecreaseCopies
AFTER INSERT ON Borrowing
WHEN NEW.Status = 'Borrowed'
BEGIN
    UPDATE Books SET Copies_Available = Copies_Available - 1 WHERE Book_ID = NEW.Book_ID;
END;

CREATE TRIGGER trg_IncreaseCopies
AFTER UPDATE ON Borrowing
WHEN NEW.Status = 'Returned' AND OLD.Status = 'Borrowed'
BEGIN
    UPDATE Books SET Copies_Available = Copies_Available + 1 WHERE Book_ID = NEW.Book_ID;
END;
"""

BOOKS = [
    ("1984", "George Orwell", "Dystopian", "9780451524935", 3,
     {"publisher": "Secker & Warburg", "edition": "1st", "year": 1949,
      "summary": "Dystopian future surveillance state."}),
    ("Brave New World", "Aldous Huxley", "Science Fiction", "9780060850524", 5,
     {"publisher": "Chatto & Windus", "edition": "1st", "year": 1932,
      "summary": "A futuristic world with genetically modified citizens."}),
    ("Suç ve Ceza", "Fyodor Dostoyevski", "Roman", "9786254481282", 5,
     {"language": "Rusça", "pages": 671, "publisher": "Can Yayınları", "year": 1866}),
    ("Sefiller", "Victor Hugo", "Roman", "9786053322646", 4,
     {"language": "Fransızca", "pages": 1232, "publisher": "İthaki Yayınları", "year": 1862}),
    ("Don Kişot", "Miguel de Cervantes", "Macera", "9786257050669", 3,
     {"language": "İspanyolca", "pages": 1023, "publisher": "İş Bankası Kültür Yayınları", "year": 1605}),
    ("İki Şehrin Hikayesi", "Charles Dickens", "Tarihî Roman", "9789750700962", 4,
     {"language": "İngilizce", "pages": 489, "publisher": "Can Yayınları", "year": 1859}),
    ("Anna Karenina", "Lev Tolstoy", "Trajik Roman", "9789754589938", 5,
     {"language": "Rusça", "pages": 864, "publisher": "Türkiye İş Bankası", "year": 1877}),
]

STUDENTS = [
    ("Ali Yılmaz", "ali@example.com", "Computer Engineering"),
    ("Ayşe Demir", "ayse@example.com", "Industrial Engineering"),
    ("Mehmet Kaya", "mehmet@example.com", "Mechanical Engineering"),
    ("Zeynep Çelik", "zeynep@example.com", "Electrical Engineering"),
    ("Can Öztürk", "can@example.com", "Software Engineering"),
]

REVIEWS = [
    (1, 1, 5, "Distopik bir başyapıt, herkesin okuması lazım."),
    (1, 3, 4, "Etkileyici ama biraz karanlık."),
    (3, 2, 5, "Uzun ama değdi, karakterler çok derin."),
    (7, 5, 4, "Tolstoy'un anlatımı müthiş."),
]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    cur = conn.cursor()
    for title, author, genre, isbn, copies, meta in BOOKS:
        cur.execute(
            "INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata) VALUES (?,?,?,?,?,?)",
            (title, author, genre, isbn, copies, json.dumps(meta, ensure_ascii=False)),
        )
    for name, email, major in STUDENTS:
        cur.execute(
            "INSERT INTO Students (Name, Email, Major) VALUES (?,?,?)",
            (name, email, major),
        )
    for book_id, student_id, rating, comment in REVIEWS:
        cur.execute(
            "INSERT INTO Reviews (Book_ID, Student_ID, Rating, Comment) VALUES (?,?,?,?)",
            (book_id, student_id, rating, comment),
        )

    # one sample active loan, and one overdue loan, to demo the UI right away
    cur.execute("""
        INSERT INTO Borrowing (Book_ID, Student_ID, Borrow_Date, Due_Date, Status)
        VALUES (2, 4, date('now', '-3 days'), date('now', '+11 days'), 'Borrowed')
    """)
    cur.execute("""
        INSERT INTO Borrowing (Book_ID, Student_ID, Borrow_Date, Due_Date, Status)
        VALUES (5, 2, date('now', '-20 days'), date('now', '-6 days'), 'Borrowed')
    """)

    conn.commit()
    conn.close()
    print(f"✓ library.db created at {DB_PATH} with {len(BOOKS)} books, {len(STUDENTS)} students, "
          f"{len(REVIEWS)} reviews, and 2 sample loans.")


if __name__ == "__main__":
    main()