import pytest
from library_service import add_book_to_catalog, borrow_book_by_patron, return_book_by_patron, get_patron_status_report
from database import get_book_by_isbn, insert_borrow_record

def add_book(title, author, isbn, copies = 1):
    result, output = add_book_to_catalog(title, author, isbn, copies)
    assert result
    return get_book_by_isbn(isbn)

def test_empty_patron():
    status = get_patron_status_report("124323")
    for i in ["current_loans", "total_late_fees", "borrowed_count", "history"]:
        assert i in status
    assert isinstance(status["current_loans"], list)
    assert isinstance(status["history"], list)
    assert status["borrowed_count"] == 0
    assert float(status["total_late_fees"]) == 0.0

def test_current_loans_and_count():
    patron = "293827"
    test_book1 = add_book("The Park", "Jay", "2321322123456")
    test_book2 = add_book("Kings", "Marty", "2919928173828")

    assert borrow_book_by_patron(patron, test_book1["id"])[0]
    assert borrow_book_by_patron(patron, test_book2["id"])[0]

    status = get_patron_status_report(patron)
    assert status["borrowed_count"] == 2
    titles = [i.get("title") for i in status["current_loans"]]
    assert "The Park" in titles and "Kings" in titles
    for row in status["current_loans"]:
        assert "due_date" in row and row["due_date"]

def test_loans_to_history():
    patron = "321321"
    test_book = add_book("Batman", "Wayne", "2839219302124")
    assert borrow_book_by_patron(patron, test_book["id"])[0]
    assert return_book_by_patron(patron, test_book["id"])[0]

    status = get_patron_status_report(patron)
    current_loans = [i["title"] for i in status["current_loans"]]
    history = [i["title"] for i in status["history"]]
    assert "Batman" not in current_loans
    assert "Batman" in history

def test_total_late_fees_when_overdue():
    patron = "291834"
    test_book = add_book("Superman", "Steve", "1283819301932")
    borrow_date = "2024-01-01"
    due_date    = "2024-01-15"
    assert insert_borrow_record(patron, test_book["id"], borrow_date, due_date)

    status = get_patron_status_report(patron)
    assert float(status["total_late_fees"]) > 0.0

    status = get_patron_status_report(patron)
    assert float(status["total_late_fees"]) > 0.0

def test_bad_patron_id_handler():
    for pid in ["", "32123", "3212442", "83u823"]:
        status = get_patron_status_report(pid)
        if isinstance(status, dict):
            for i in ["current_loans", "total_late_fees", "borrowed_count", "history"]:
                assert i in status
        else:
            assert status is not None