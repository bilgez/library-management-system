import sqlite3
import json
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

app = Flask(__name__)
app.secret_key = "library-project-demo"  # fine for a local demo, not production


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@app.route("/")
def catalog():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    conn = get_db()

    query = "SELECT * FROM Books WHERE 1=1"
    params = []
    if q:
        query += " AND (Title LIKE ? OR Author LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if genre:
        query += " AND Genre = ?"
        params.append(genre)
    query += " ORDER BY Title"

    books = conn.execute(query, params).fetchall()
    genres = [r["Genre"] for r in conn.execute("SELECT DISTINCT Genre FROM Books ORDER BY Genre")]
    conn.close()
    return render_template("catalog.html", books=books, genres=genres, q=q, active_genre=genre)


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM Books WHERE Book_ID = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        return "Book not found", 404

    reviews = conn.execute("""
        SELECT r.*, s.Name AS StudentName
        FROM Reviews r JOIN Students s ON r.Student_ID = s.Student_ID
        WHERE r.Book_ID = ? ORDER BY r.Created_At DESC
    """, (book_id,)).fetchall()

    students = conn.execute("SELECT * FROM Students ORDER BY Name").fetchall()
    avg_rating = conn.execute(
        "SELECT AVG(Rating) AS avg FROM Reviews WHERE Book_ID = ?", (book_id,)
    ).fetchone()["avg"]

    conn.close()
    metadata = json.loads(book["Metadata"]) if book["Metadata"] else {}
    return render_template(
        "book_detail.html", book=book, reviews=reviews, students=students,
        avg_rating=round(avg_rating, 1) if avg_rating else None, metadata=metadata
    )


@app.route("/book/<int:book_id>/borrow", methods=["POST"])
def borrow(book_id):
    student_id = request.form.get("student_id")
    conn = get_db()
    book = conn.execute("SELECT * FROM Books WHERE Book_ID = ?", (book_id,)).fetchone()

    if not book or book["Copies_Available"] <= 0:
        flash("Bu kitabın şu anda uygun kopyası yok.", "error")
        conn.close()
        return redirect(url_for("book_detail", book_id=book_id))

    conn.execute("""
        INSERT INTO Borrowing (Book_ID, Student_ID, Borrow_Date, Due_Date, Status)
        VALUES (?, ?, date('now'), date('now', '+14 days'), 'Borrowed')
    """, (book_id, student_id))
    conn.commit()
    conn.close()
    flash(f"'{book['Title']}' ödünç alındı — 14 gün içinde iade edilmeli.", "success")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/book/<int:book_id>/review", methods=["POST"])
def add_review(book_id):
    student_id = request.form.get("student_id")
    rating = request.form.get("rating")
    comment = request.form.get("comment", "").strip()
    conn = get_db()
    conn.execute(
        "INSERT INTO Reviews (Book_ID, Student_ID, Rating, Comment) VALUES (?,?,?,?)",
        (book_id, student_id, rating, comment)
    )
    conn.commit()
    conn.close()
    flash("Yorumun eklendi, teşekkürler!", "success")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/loans")
def loans():
    conn = get_db()
    active = conn.execute("""
        SELECT bo.*, bk.Title, s.Name AS StudentName,
               (julianday('now') - julianday(bo.Due_Date)) AS days_overdue
        FROM Borrowing bo
        JOIN Books bk ON bo.Book_ID = bk.Book_ID
        JOIN Students s ON bo.Student_ID = s.Student_ID
        WHERE bo.Status = 'Borrowed'
        ORDER BY bo.Due_Date ASC
    """).fetchall()
    history = conn.execute("""
        SELECT bo.*, bk.Title, s.Name AS StudentName
        FROM Borrowing bo
        JOIN Books bk ON bo.Book_ID = bk.Book_ID
        JOIN Students s ON bo.Student_ID = s.Student_ID
        WHERE bo.Status = 'Returned'
        ORDER BY bo.Return_Date DESC LIMIT 10
    """).fetchall()
    conn.close()
    return render_template("loans.html", active=active, history=history, today=date.today().isoformat())


@app.route("/loans/<int:borrow_id>/return", methods=["POST"])
def return_book(borrow_id):
    conn = get_db()
    record = conn.execute("SELECT * FROM Borrowing WHERE Borrow_ID = ?", (borrow_id,)).fetchone()
    if not record or record["Status"] == "Returned":
        flash("Bu ödünç kaydı bulunamadı ya da zaten iade edilmiş.", "error")
        conn.close()
        return redirect(url_for("loans"))

    conn.execute(
        "UPDATE Borrowing SET Status = 'Returned', Return_Date = date('now') WHERE Borrow_ID = ?",
        (borrow_id,)
    )
    conn.commit()
    conn.close()
    flash("Kitap iade edildi.", "success")
    return redirect(url_for("loans"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("⚠️  library.db not found — run `python init_db.py` first.")
    app.run(debug=True, port=5050)