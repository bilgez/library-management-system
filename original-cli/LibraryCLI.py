import pyodbc
import pandas as pd
from pymongo import MongoClient

# ----------SQL Server Connection and Helper Functions -----------

def get_connection():
    server = 'localhost'
    database = 'LibraryDB'
    connection_string = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)

def list_books():
    try:
        with get_connection() as conn:
            query = "SELECT Book_ID, Title, Author, Copies_Available FROM Books"
            df = pd.read_sql_query(query, conn)
            if df.empty:
                print("📭 There are no books in the library.")
            else:
                print("\n📚 Book List:\n")
                print(df.to_string(index=False))
    except pyodbc.Error as e:
        print("❌ SQL Server error:", e)

def search_books():
    keyword = input("🔍 Enter the book title you want to search: ").strip()
    if not keyword:
        print("❗ Boş arama yapılamaz.")
        return
    try:
        with get_connection() as conn:
            query = "SELECT Book_ID, Title, Author, Copies_Available FROM Books WHERE Title LIKE ?"
            df = pd.read_sql_query(query, conn, params=(f"%{keyword}%",))
            if df.empty:
                print("📭 No books were found matching your search.")
            else:
                print("\n📚 Search Results:\n")
                print(df.to_string(index=False))
    except pyodbc.Error as e:
        print("❌ SQL Server hatası:", e)

# ----------- MongoDB Connection and Comment Function ----------------

def connect_mongo():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["LibraryDB"]
        comments_col = db["book_reviews"]  
        return comments_col
    except Exception as e:
        print("❌ MongoDB bağlantı hatası:", e)
        return None


def show_comments():
    book_id = input("💬 Enter the ID of the book you want to see reviews for: ").strip()

    comments_col = connect_mongo()
    if comments_col is not None:
        results = comments_col.find({"book_id": book_id})  
        print(f"\n💬 Book ID {book_id} Comments for:")
        found = False
        for comment in results:
            found = True
            print(f"- 👤 Student ID {comment.get('student_id', 'unknown')}: {comment.get('comment', '')} ⭐({comment.get('rating', 'N/A')})")

        if not found:
            print("📭 No comments found for this book.")


# ----------- Borrowing Function ----------------

def get_books():
    try:
        with get_connection() as conn:
            query = "SELECT Book_ID, Title, Copies_Available FROM Books"
            df = pd.read_sql_query(query, conn)
            return df
    except pyodbc.Error as e:
        print("❌ Could not get book list: ", e)
        return None

def borrow_book():
    df = get_books()
    if df is None or df.empty:
        print("📭 There are no books in the library.")
        return

    try:
        book_id = int(input("📘 Enter the ID of the book you want to borrow: ").strip())
        student_id = int(input("👤 Enter Student ID: ").strip())
    except ValueError:
        print("❌ Please enter a valid number.")
        return

    book_row = df[df['Book_ID'] == book_id]
    if book_row.empty:
        print("❌ No book found for this ID.")
        return

    copies = int(book_row['Copies_Available'].values[0])
    title = book_row['Title'].values[0]

    if copies <= 0:
        print(f"⚠️ '{title}' currently out of stock. ")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Students WHERE Student_ID = ?", student_id)
            student = cursor.fetchone()
            if not student:
                print("❌ This student ID was not found in the database.")
                return

            cursor.execute("UPDATE Books SET Copies_Available = Copies_Available - 1 WHERE Book_ID = ?", book_id)
            cursor.execute("INSERT INTO Borrowing (Book_ID, Student_ID, Borrow_Date, Status) VALUES (?, ?, GETDATE(), 'Borrowed')", book_id, student_id)

            conn.commit()
            print(f"✅ '{title}' was borrowed successfully.")
    except pyodbc.Error as e:
        print("❌ An error occurred while borrowing: ", e)

# ----------- Book Return Function ----------------

def return_book():
    try:
        borrow_id = int(input("📗 Enter the loan ID you wish to return: ").strip())
    except ValueError:
        print("❌ Please enter a valid number.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT Book_ID, Status FROM Borrowing WHERE Borrow_ID = ?", borrow_id)
            record = cursor.fetchone()
            if not record:
                print("❌ No record found for this loan.")
                return

            book_id = record[0]
            status = record[1]

            if status.lower() == 'returned':
                print("⚠️ This book has already been returned.")
                return

            cursor.execute(
                "UPDATE Borrowing SET Return_Date = GETDATE(), Status = 'returned' WHERE Borrow_ID = ?", borrow_id
            )
            cursor.execute(
                "UPDATE Books SET Copies_Available = Copies_Available + 1 WHERE Book_ID = ?", book_id
            )
            conn.commit()
            print("✅ The book return process was successful.")
    except pyodbc.Error as e:
        print("❌ An error occurred during the return process:", e)


# ----------- List Overdue Books ----------------

def list_overdue_books():
    try:
        with get_connection() as conn:
            query = """
            SELECT b.Borrow_ID, bk.Title, s.Name, b.Borrow_Date, b.Return_Date, b.Status
            FROM Borrowing b
            JOIN Books bk ON b.Book_ID = bk.Book_ID
            JOIN Students s ON b.Student_ID = s.Student_ID
            WHERE b.Status = 'borrowed' AND b.Borrow_Date < DATEADD(day, -14, GETDATE())
            """
            df = pd.read_sql_query(query, conn)
            if df.empty:
                print("📭 No overdue books.")
            else:
                print("\n⏰ Overdue Books (over 14 days):")
                print(df.to_string(index=False))
    except pyodbc.Error as e:
        print("❌ An error occurred during the query for overdue books:", e)
        

# ----------- Main Menu ----------------

def main_menu():
    while True:
        print("""
===== Library Management System =====

1 - List Books
2 - Search Books
3 - Borrow Books
4 - Return Books
5 - Show Book Reviews
6 - List Overdue Books
7 - Exit
""")
        choice = input("Your choice: ").strip()

        if choice == '1':
            list_books()
        elif choice == '2':
            search_books()
        elif choice == '3':
            borrow_book()
        elif choice == '4':
            return_book()
        elif choice == '5':
            show_comments()
        elif choice == '6':
            list_overdue_books()
        elif choice == '7':
            print("Checking out... See you!")
            break
        else:
            print("❗Invalid selection, please try again.")

if __name__ == "__main__":
    main_menu()