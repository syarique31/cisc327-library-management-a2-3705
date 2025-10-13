"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_db_connection, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits and contain only numbers."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books." ############################
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(
        patron_id, 
        book_id, 
        borrow_date,
        due_date
    )
    
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:

    if not patron_id or not patron_id.isdigit() or len(patron_id) !=6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    db_conn = get_db_connection()
    full_record = db_conn.execute("""
        SELECT * FROM borrow_records
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (patron_id, book_id)).fetchone()
    db_conn.close()

    if not full_record:
        return False, "This book was not borrowed by this patron or has already been returned."
    
    fee = calculate_late_fee_for_book(patron_id, book_id)

    update = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not update:
        return False, "There is no record of this borrowed book from this patron ID"

    update_book_availability(book_id, +1)
    
    return True, f'Book "{book["title"]}" has been returned successfully. Late fee: ${fee["fee_amount"]:.2f}'

    

    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    return False, "Book return functionality is not yet implemented."

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    db_conn = get_db_connection()

    query_record = db_conn.execute("""
        SELECT due_date
        FROM borrow_records
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (patron_id, book_id)).fetchone()
    db_conn.close()

    if not query_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book cannot be found'
        }

    due_date = datetime.fromisoformat(query_record['due_date'])
    current_date = datetime.now()
    days_overdue = (current_date - due_date).days

    if days_overdue <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Returned on time'
        }

    first_week_late_fee = min(days_overdue, 7) * 0.5
    additional_late_fee = max(days_overdue - 7, 0) * 1.0
    late_fee = min(first_week_late_fee + additional_late_fee, 15.0)
    return {
        'fee_amount': round(late_fee, 2),
        'days_overdue': days_overdue,
        'status': 'Late fee calculated successfully'
    }

    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:

    results = []
    search_for_term = search_term.strip().lower()
    every_books = get_all_books()

    for books in every_books:
        if search_type == "title" and search_for_term in books["title"].lower():
            results.append(books)
        elif search_type == "author" and search_for_term in books["author"].lower():
            results.append(books)
        elif search_type == "isbn" and search_for_term == books["isbn"].lower():
            results.append(books)

    return results


    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """

def get_patron_status_report(patron_id: str) -> Dict:

    if not patron_id or not patron_id.isdigit() or len(patron_id) !=6:
          return {
            "patron_id": patron_id,
            "currently_borrowed": 0,
            "borrowed_count": 0,
            "total_late_fees": 0.0,
            "current_loans": [],
            "history": [],
            "status": "Invalid ID"
        }
    
    current_books = get_patron_borrowed_books(patron_id)
    num_of_current_books = len(current_books)
    current_date = datetime.now().date()    


    late_fee = 0.0
    for i in current_books:
        due = i["due_date"].date()
        days_overdue  = max(0, (current_date-due).days)
        if days_overdue > 0:
            late_fee += min(days_overdue * 0.5, 15.0)
    
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT b.title, b.author, br.borrow_date, br.return_date
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date DESC
    """, (patron_id,)).fetchall()
    conn.close()

    full_history = []
    for row in rows:
        full_history.append({
            "title": row["title"],
            "author": row["author"],
            "borrow_date": row["borrow_date"],
            "return_date": row["return_date"] or "This book has not yet been returned"
        })

    report_on_patron = {
        "patron_id" : patron_id,
        "currently_borrowed" : num_of_current_books,
        "borrowed_count": num_of_current_books,
        "total_late_fees" : round(late_fee , 2), 
        "current_loans" : current_books,
        "history" : full_history,
        "status" : "Active" if num_of_current_books < 5 else "At borrowing limit"
    }

    return report_on_patron

    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    
