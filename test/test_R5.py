import pytest
from library_service import add_book_to_catalog, calculate_late_fee_for_book
from database import get_book_by_isbn, insert_borrow_record

def add_book(isbn: str, copies: int = 1):
    result, output = add_book_to_catalog("Wings of Fire", "King", isbn, copies)
    assert result
    return get_book_by_isbn(isbn)

def borrow_book(patron_id: str, book_id: int, borrow_date: str, due_date: str):
    assert insert_borrow_record(patron_id, book_id, borrow_date, due_date)

def test_fee_on_time():
    test_book = add_book("1828183716341")
    borrow_book("492814", test_book["id"], "2024-01-01", "2100-01-01")
    fee_info = calculate_late_fee_for_book("492814", test_book["id"])
    assert fee_info["days_overdue"] == 0
    assert float(fee_info["fee_amount"]) == 0.00

def test_fee_overdue():
    test_book = add_book("1928173718342")
    borrow_book("153214", test_book["id"], "2000-01-01", "2000-01-15")
    fee_info = calculate_late_fee_for_book("153214", test_book["id"])
    assert fee_info["days_overdue"] > 0
    assert float(fee_info["fee_amount"]) > 0.00

def test_fee_max_cap():
    test_book = add_book("1049938472718")
    borrow_book("193845", test_book["id"], "1990-01-01", "1990-01-15")
    fee_info = calculate_late_fee_for_book("193845", test_book["id"])
    assert fee_info["days_overdue"] > 20
    assert float(fee_info["fee_amount"]) == 15.00

def test_fee_no_record():
    test_book = add_book("1837482813212")
    fee_info = calculate_late_fee_for_book("194837", test_book["id"])
    if {"fee_amount", "days_overdue"} <= set(fee_info.keys()):
        assert fee_info["days_overdue"] == 0
        assert float(fee_info["fee_amount"]) == 0.00
    else:
        assert "error" in fee_info or "message" in fee_info


#new test case

def test_fee_invalid_book_id():
    fee_info = calculate_late_fee_for_book("123456", 122343)
    assert fee_info["fee_amount"] == 0.00
    assert fee_info["days_overdue"] == 0
    assert "Book cannot be found" in fee_info["status"]