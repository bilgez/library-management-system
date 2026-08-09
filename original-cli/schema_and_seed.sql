-- Creation of Database
CREATE DATABASE LibraryDB;
GO
USE LibraryDB;
GO

-- 1. Books Table
CREATE TABLE Books (
    Book_ID INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(255),
    Author NVARCHAR(255),
    Genre NVARCHAR(100),
    ISBN NVARCHAR(20),
    Copies_Available INT,
    Metadata NVARCHAR(MAX) -- JSON destekli alan (SQL Server'da JSON string olarak tutulur)
);

-- 2. Students Table
CREATE TABLE Students (
    Student_ID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(255),
    Email NVARCHAR(100),
    Major NVARCHAR(100)
);

-- 3. Borrowing Table
CREATE TABLE Borrowing (
    Borrow_ID INT PRIMARY KEY IDENTITY(1,1),
    Book_ID INT FOREIGN KEY REFERENCES Books(Book_ID),
    Student_ID INT FOREIGN KEY REFERENCES Students(Student_ID),
    Borrow_Date DATE,
    Return_Date DATE,
    Status NVARCHAR(20) -- using 'Borrowed'/ 'Returned' 
);

-- 4. Librarians Table
CREATE TABLE Librarians (
    Librarian_ID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(255),
    Email NVARCHAR(100)
);

-------------------------------------------

GO
CREATE TRIGGER trg_DecreaseCopies
ON Borrowing
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Books
    SET Copies_Available = Copies_Available - 1
    FROM Books
    INNER JOIN inserted i ON Books.Book_ID = i.Book_ID
    WHERE i.Status = 'Borrowed';
END;
GO

GO
CREATE TRIGGER trg_IncreaseCopies
ON Borrowing
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Books
    SET Copies_Available = Copies_Available + 1
    FROM Books
    INNER JOIN inserted i ON Books.Book_ID = i.Book_ID
    WHERE i.Status = 'Returned';
END;
GO

-------------------------Students Records--------------------------------
-- Student 1 
INSERT INTO Students (Name, Email, Major)
VALUES ('Ali Yılmaz', 'ali@example.com', 'Computer Engineering');
SELECT * FROM Students;

-- Student 2
INSERT INTO Students (Name, Email, Major)
VALUES ('Ayşe Demir', 'ayse@example.com', 'Industrial Engineering');

-- Student 3
INSERT INTO Students (Name, Email, Major)
VALUES ('Mehmet Kaya', 'mehmet@example.com', 'Mechanical Engineering');

-- Student 4
INSERT INTO Students (Name, Email, Major)
VALUES ('Zeynep Çelik', 'zeynep@example.com', 'Electrical Engineering');

-- Student 5
INSERT INTO Students (Name, Email, Major)
VALUES ('Can Öztürk', 'can@example.com', 'Software Engineering');

-------------------------------------------------------------------------------------------------------------

-- Borrowing
INSERT INTO Borrowing (Book_ID, Student_ID, Borrow_Date, Return_Date, Status)
VALUES (1, 1, GETDATE(), DATEADD(DAY, 7, GETDATE()), 'Borrowed');

-- Returned
UPDATE Borrowing
SET Status = 'Returned'
WHERE Borrow_ID = 1;


-------------------------------

GO
CREATE PROCEDURE sp_ListOverdueBooks
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        b.Borrow_ID,
        s.Name AS StudentName,
        bk.Title AS BookTitle,
        b.Borrow_Date,
        b.Return_Date
    FROM Borrowing b
    INNER JOIN Students s ON b.Student_ID = s.Student_ID
    INNER JOIN Books bk ON b.Book_ID = bk.Book_ID
    WHERE b.Status = 'Borrowed' AND b.Return_Date < GETDATE();
END;
GO

-----------------XML usage---------------------

SELECT 
    b.Borrow_ID,
    b.Book_ID,
    b.Student_ID,
    b.Borrow_Date,
    b.Return_Date,
    b.Status
FROM Borrowing b
FOR XML PATH('Borrowing'), ROOT('BorrowingRecords');

--------------------------------
SELECT 
    Title,
    Author,
    JSON_VALUE(Metadata, '$.publisher') AS Publisher,
    JSON_VALUE(Metadata, '$.edition') AS Edition
FROM Books;


SELECT 
    Title,
    Author
FROM Books
WHERE JSON_VALUE(Metadata, '$.publisher') = 'Secker & Warburg';


SELECT 
    Title,
    JSON_VALUE(Metadata, '$.summary') AS Summary
FROM Books;


---------------------------------------------- Books Records ------------------------------------------

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    '1984',
    'George Orwell',
    'Dystopian',
    '9780451524935',
    3,
    '{
        "publisher": "Secker & Warburg",
        "edition": "1st",
        "summary": "Dystopian future surveillance state."
    }'
);

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'Brave New World',
    'Aldous Huxley',
    'Science Fiction',
    '9780060850524',
    5,
    '{
        "publisher": "Chatto & Windus",
        "edition": "1st",
        "summary": "A futuristic world with genetically modified citizens."
    }'
);
INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'Suç ve Ceza',
    'Fyodor Dostoyevski',
    'Roman',
    '9786254481282',
    5,
    '{
        "language": "Rusça",
        "pages": 671,
        "publisher": "Can Yayınları",
        "year": 1866
    }'
);

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'Sefiller',
    'Victor Hugo',
    'Roman',
    '9786053322646',
    4,
    '{
        "language": "Fransızca",
        "pages": 1232,
        "publisher": "İthaki Yayınları",
        "year": 1862
    }'
);

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'Don Kişot',
    'Miguel de Cervantes',
    'Macera',
    '9786257050669',
    3,
    '{
        "language": "İspanyolca",
        "pages": 1023,
        "publisher": "İş Bankası Kültür Yayınları",
        "year": 1605
    }'
);

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'İki Şehrin Hikayesi',
    'Charles Dickens',
    'Tarihî Roman',
    '9789750700962',
    4,
    '{
        "language": "İngilizce",
        "pages": 489,
        "publisher": "Can Yayınları",
        "year": 1859
    }'
);

INSERT INTO Books (Title, Author, Genre, ISBN, Copies_Available, Metadata)
VALUES (
    'Anna Karenina',
    'Lev Tolstoy',
    'Trajik Roman',
    '9789754589938',
    5,
    '{
        "language": "Rusça",
        "pages": 864,
        "publisher": "Türkiye İş Bankası",
        "year": 1877
    }'
);