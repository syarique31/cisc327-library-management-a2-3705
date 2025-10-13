from library_service import add_book_to_catalog

def test_add_success():
    result, output = add_book_to_catalog("Book_Test", "Syarique Izzat", "0392818291924", 3) #this test case will check whether the book added to the catalog is successful
    assert result
    assert "success" in output.lower()

def test_title_max_length():
    result, output = add_book_to_catalog("x"*201, "Author", "1234567890123", 1) #this test case  will check whether max length of the book title can reached the max more than 200 characters
    assert not result and "200" in output

def test_author_max_length():
    result, output = add_book_to_catalog("Hunger Games", "X"*101, "1231233213421", 1)  #this test case  will check whether max length of the author name can reached the max more than 100 characters
    assert not result and "100" in output

def test_author_100_boundary_ok():
    result, output = add_book_to_catalog("Masterchief", "X"*100, "5555555555556", 1) # #this test case  will check whether the number of characters below the max is success, of 100 characters
    assert result

def test_isbn_wrong_length():
    test_case = ["123", "123456789012", "12345678941234"]
    for isbn in test_case:
        result, output = add_book_to_catalog("Theory Master", "Alexander", isbn, 1) #this test case  checks the validation for ISBN number length, ensuring it always 13 digits, rather than anything more or less
        assert not result
        assert "13 digits" in output

def test_empty_title():
    result, output = add_book_to_catalog("", "Alex", "1112342131234", 1) #this test case will check whether you are allowed to write an empty book title to the catalog
    assert not result
    assert "title is required" in output.lower()

def test_author_required():
    result, output = add_book_to_catalog("Lego Movie", "", "5555555555555", 1) #this test case will check whether the website will allow the new submission to the catalog of the book lego movie is allowed to be entered without an author name
    assert not result
    assert "author is required" in output.lower()

def test_isbn_digits_only_check():
    result, output = add_book_to_catalog("Big Nate", "Bell", "1234567u90132", 1) #this test case will check whether ISBN digit is allowed an input of an alphabet, rather than just strictly 13 digit ISBN number
    assert not result
    assert "13 digits" in output  

def test_title_200_boundary_ok():
    result, output = add_book_to_catalog("x"*200, "Cameron", "3821727382813", 1) # #this test case  will check whether the number of characters below the max is success, of 200 characters
    assert result

def test_non_positive_total_copies():
    for i in [0, -2, 5.5]:
        result, output = add_book_to_catalog("test test", "James", "8172638478219", i) #this test case will check if you can add non positive digits for the total copies of the book
        assert not result

def test_duplicate_isbn():
    result, output = add_book_to_catalog("Book test", "Neil", "1231231234678", 1) #this test case will check if you can submit a second book thats not the same title from the first book added, but with the same ISBN number
    assert result
    result2, msg2 = add_book_to_catalog("Book test2", "Lola", "1231231234678", 2)
    assert not result2
    assert "already exists" in msg2.lower()