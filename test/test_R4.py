import pytest
from library_service import add_book_to_catalog, borrow_book_by_patron, return_book_by_patron
from database import get_book_by_isbn, get_book_by_id, insert_borrow_record

def add_book(isbn: str, copies: int = 1):
    result, output = add_book_to_catalog("Geronimo Stilton", "Himself", isbn, copies)
    assert result, "Book insert failed"
    return get_book_by_isbn(isbn)

def test_return_book_ontime():
    test_book = add_book("9283610092381", copies=1)
    result, output = borrow_book_by_patron("928374", test_book["id"])
    assert result
    result, output = return_book_by_patron("928374", test_book["id"])
    assert result
    assert get_book_by_id(test_book["id"])["available_copies"] == 1
    assert "late fee" in output.lower()
    assert "0.00" in output  

def test_return_book_from_wrong_patron_ID():
    test_book = add_book("9382736154324", copies=1)
    result, output = borrow_book_by_patron("838283", test_book["id"])
    assert result
    result, output = return_book_by_patron("111111", test_book["id"])
    assert not result
    assert "not borrowed by this patron" in output.lower()

def test_return_book_twice():
    test_book = add_book("0392839291832", copies=1)
    result, output = borrow_book_by_patron("444444", test_book["id"])
    assert result
    result, output = return_book_by_patron("444444", test_book["id"])
    assert result
    result, output = return_book_by_patron("444444", test_book["id"])
    assert not result
    assert "returned" in output.lower()

def test_return_non_borrowed_book():
    test_book = add_book("9402938591843", copies=1)
    result, output = return_book_by_patron("938273", test_book["id"])
    assert not result
    assert "not borrowed" in output.lower() 

def test_return_invalid_id():
    test_book = add_book("1838281721832", copies=1)
    result, output = borrow_book_by_patron("192819", test_book["id"])
    assert result

    for i in ["12a456", "12345", "1234567", ""]:
        result2, output2 = return_book_by_patron(i, test_book["id"])
        assert not result2
        assert "6" in output2 or "invalid" in output2.lower()

def test_return_DNE_book_ID():
    result, output = return_book_by_patron("124212", 999999999)
    assert not result
    assert "not found" in output.lower() or "no record" in output.lower()

def test_book_return_overdue_fee():
    test_book = add_book("1928281392010", copies=1)

    borrow_date = "2020-01-01"
    due_date = "2020-01-15"

    insert_borrow_record("124521", test_book["id"], borrow_date, due_date)

    result, output = return_book_by_patron("124521", test_book["id"])
    assert result
    assert "late fee" in output.lower()
    assert "0.00" not in output

#new test case

def test_book_not_borrowed_record():
    test_book = add_book("9999293929310", copies=1)

    result, output = return_book_by_patron("123456", test_book["id"])

    assert not result
    assert "no record" in output.lower() or "not borrowed" in output.lower()