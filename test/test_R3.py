import pytest
from library_service import borrow_book_by_patron, add_book_to_catalog
from database import get_book_by_isbn

def add_book(isbn: str, copies: int = 1):
    add_book_to_catalog("Hardy Boys", "Pam", isbn, copies) 
    return get_book_by_isbn(isbn)

def test_book_borrow_success():
    test_book = add_book("3000000000001", copies=5)
    result, output = borrow_book_by_patron("123456", test_book["id"])
    assert result
    assert "due date" in output.lower()

def test_no_more_copies():
    test_book = add_book("3000000000003", copies=2) #test with 2 copies
    
    result, output = borrow_book_by_patron("111111", test_book["id"])
    assert result

    result, output = borrow_book_by_patron("333333", test_book["id"])
    assert result

    result, output = borrow_book_by_patron("222222", test_book["id"]) #no more copies
    assert not result
    assert "not available" in output.lower()

def test_invalid_patron_id():
    test_book = add_book("1838281828183", copies=1)
    bad_test_ids = ["", "95939", "1992k382"]
    for i in bad_test_ids:
        result, output = borrow_book_by_patron(i, test_book["id"])
        assert not result
        assert "6 digits" in output

def test_success_message_has_due_date():
    test_book = add_book("3821938281832", copies=1)
    result, output = borrow_book_by_patron("123942", test_book["id"])
    assert result
    assert "due date" in output.lower()

def test_borrow_DNE_book_id():
    result, output = borrow_book_by_patron("999999", 9999999999999)  
    assert not result
    assert "not found" in output.lower()

def test_available_copies_decrease():
    test_book = add_book("3829183828173", copies = 2)
    take_book = get_book_by_isbn("3829183828173")["available_copies"]
    result, output = borrow_book_by_patron("391843", test_book["id"])
    take_book_again = get_book_by_isbn("3829183828173")["available_copies"]
    assert result
    assert take_book_again == take_book - 1

def test_limit_books_borrowed():
    for i in range(5):
        test_book = add_book(f"300000000000{i+4}")
        result, output = borrow_book_by_patron("999999", test_book["id"])
        assert result

    sixth_book =add_book("3000000000010")  
    result, output = borrow_book_by_patron("999999", sixth_book["id"])
    assert not result
    assert "max" in output.lower() or "limit" in output.lower()
  

