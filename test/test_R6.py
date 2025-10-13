import pytest
from library_service import add_book_to_catalog, search_books_in_catalog
from database import get_book_by_isbn

def add_book(title, author, isbn, copies = 3):
    result, output = add_book_to_catalog(title, author, isbn, copies)
    assert result
    return get_book_by_isbn(isbn)

def test_search_title():
    test_book1 = add_book("Lord of the Rings", "Tony", "1928173829381")
    test_book2 = add_book("Middle School", "Patterson", "1824828182912")
    add_book("Scorch Trials", "James", "2382818382913")

    results = search_books_in_catalog("lor", "title")
    results_id = [i["id"] for i in results]
    assert test_book1["id"] in results_id
    assert test_book2["id"] not in results_id

def test_search_author_partially():
    test_book1 = add_book("Hobbit", "Harper Griffin", "2837183728173")
    test_book2 = add_book("Harry Potter", "Griffin, Lee", "9933762638177")
    
    results = search_books_in_catalog("GRiFfIn", "author")
    names = [(i["title"], i["author"]) for i in results]
    assert ("Hobbit", "Harper Griffin") in names
    assert ("Harry Potter", "Griffin, Lee") in names

def test_find_exact_isbn():
    test_book1 = add_book("Cleaners", "Rob", "1928377221722")
    add_book("Atomic Habits", "Stacy", "1233482839219")

    results = search_books_in_catalog("1928377221722", "isbn")
    assert len(results) == 1
    assert results[0]["id"] == test_book1["id"]
    partial = search_books_in_catalog("1928377", "isbn")
    assert partial == [] or len(partial) == 0

def test_search_all_fields():
    add_book("Wizard of Oz", "Phillip", "1283920129219", copies = 4)
    results = search_books_in_catalog("Wizard of Oz", "title")
    assert len(results) >= 1
    row = results[0]
    for i in ["id", "title", "author", "isbn", "available_copies", "total_copies"]:
        assert i in row