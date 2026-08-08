# Library Management System — Web Version

A book catalog and lending system: search/browse books, borrow and return them, leave reviews, and track overdue loans.

This started as a team database project (`LibraryCLI.py`) — a terminal-only Python CLI backed by **SQL Server** (relational data: books, students, borrowing records) and **MongoDB** (book reviews), with SQL Server triggers keeping `Copies_Available` in sync automatically. This version rebuilds it as a proper web app.

## What changed, and why

The original CLI required both SQL Server and MongoDB running locally just to try it out — not exactly demo-friendly. For this version I:

- **Replaced SQL Server with SQLite** — same schema, same trigger logic (an `AFTER INSERT` trigger decrements `Copies_Available` when a book is borrowed, an `AFTER UPDATE` trigger restores it on return), but zero setup — it's a single file.
- **Replaced the MongoDB reviews collection with a `Reviews` table** — same idea (flexible, per-book comments and ratings), simpler to run for a portfolio demo.
- **Built an actual web interface** (Flask + Jinja templates + custom CSS) instead of a text menu.

The original SQL Server schema and CLI are preserved in this repo under `/original-cli` for reference.

## Features

- Book catalog with search and genre filtering
- Book detail pages with metadata (publisher, year, language, page count), reviews, and average rating
- Borrow a book (auto-decrements available copies via a SQLite trigger)
- Return a book (auto-restores available copies via a SQLite trigger)
- Loan tracking with automatic overdue detection (14-day loan period)
- Leave a review with a star rating

## Tech Stack

Python, Flask, SQLite (with triggers), Jinja2, vanilla CSS

## Running locally

```bash
pip install -r requirements.txt
python init_db.py      # creates library.db with schema, triggers, and sample data
python app.py           # starts the server on http://localhost:5050
```

## Project Structure

```
library-web/
├── app.py              # Flask routes
├── init_db.py            # DB schema, triggers, seed data
├── library.db             # SQLite database (generated)
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── catalog.html
│   ├── book_detail.html
│   └── loans.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Team

Originally developed as a team database project (Team 5). This web version was built by Bilge Zerda Keklik.