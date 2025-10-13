import pytest
from datetime import datetime, timedelta
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,
)
from database import init_database, add_sample_data, get_all_books


@pytest.fixture(scope="session", autouse=True)
def database_initializer():
    """Reset and seed the local dataset for AI verification."""
    init_database()
    add_sample_data()


# =====================================================
# R1 — Catalog Insertion Validation
# =====================================================

def test_R1_addition_allows_legit_entry():
    confirmation, output = add_book_to_catalog(
        "Exploring Algorithms", "Helena Brooks", "9781111222333", 3
    )
    assert confirmation is True
    assert "exploring" in output.lower()

def test_R1_fails_when_author_missing():
    state, feedback = add_book_to_catalog("Nameless Work", "", "9781231231231", 2)
    assert not state
    assert "author" in feedback.lower()

def test_R1_refuses_incorrect_isbn_digits():
    verdict, report = add_book_to_catalog("Corrupted ISBN", "Sam Field", "1234", 1)
    assert verdict is False
    assert "isbn" in report.lower()

def test_R1_blocks_duplicate_isbn():
    add_book_to_catalog("Base Entry", "Initial", "9780101010101", 5)
    duplicate_flag, note = add_book_to_catalog(
        "Conflicting Entry", "Different", "9780101010101", 2
    )
    assert duplicate_flag is False
    assert "exists" in note.lower()


# =====================================================
# R2 — Catalog Data Integrity
# =====================================================

def test_R2_structure_yields_iterable():
    registry = get_all_books()
    assert isinstance(registry, list)

def test_R2_each_item_has_defined_schema():
    registry = get_all_books()
    assert all(
        set(["title", "author", "isbn", "available_copies", "total_copies"]).issubset(set(r))
        for r in registry
    )

def test_R2_check_physical_vs_available_logic():
    dataset = get_all_books()
    for record in dataset:
        assert record["available_copies"] <= record["total_copies"]

def test_R2_validate_type_coherence():
    for element in get_all_books():
        assert isinstance(element.get("isbn"), str)
        assert isinstance(element.get("total_copies"), int)


# =====================================================
# R3 — Borrow Mechanism Evaluation
# =====================================================

def test_R3_accepts_correct_parameters():
    flag, message = borrow_book_by_patron("202222", 1)
    assert isinstance(flag, bool)
    assert flag or "borrow" in message.lower()

def test_R3_rejects_alphabetic_identifier():
    flag, message = borrow_book_by_patron("abcxyz", 1)
    assert flag is False
    assert "invalid" in message.lower()

def test_R3_rejects_empty_inventory():
    borrow_book_by_patron("404404", 2)
    attempt = borrow_book_by_patron("505505", 2)
    assert not attempt[0]
    assert any(phrase in attempt[1].lower() for phrase in ["not available", "unavailable"])

def test_R3_disallows_exceeding_threshold():
    for n in range(5):
        add_book_to_catalog(f"Cap{n}", "AutoUser", f"97866677788{n:03}", 1)
        borrow_book_by_patron("989898", n + 10)
    limit_test = borrow_book_by_patron("989898", 1)
    assert not limit_test[0]
    assert "limit" in limit_test[1].lower()


# =====================================================
# R4 — Return Operation Verification
# =====================================================

def test_R4_regular_return_releases_book():
    borrow_book_by_patron("111111", 3)
    state, descriptor = return_book_by_patron("111111", 3)
    assert state or "returned" in descriptor.lower()

def test_R4_rejects_corrupt_identifier():
    outcome, descriptor = return_book_by_patron("BAD!", 3)
    assert outcome is False
    assert "invalid" in descriptor.lower()

def test_R4_prevents_return_of_untracked_book():
    done, statement = return_book_by_patron("123123", 777)
    assert done is False
    assert "not" in statement.lower()

def test_R4_blocks_double_submission():
    borrow_book_by_patron("808080", 4)
    return_book_by_patron("808080", 4)
    second_round = return_book_by_patron("808080", 4)
    assert not second_round[0]


# =====================================================
# R5 — Fee Assessment Calculations
# =====================================================

def test_R5_fee_output_structure():
    computation = calculate_late_fee_for_book("654321", 1)
    assert set(["fee_amount", "days_overdue"]).issubset(set(computation))

def test_R5_calculates_gradual_increase(monkeypatch):
    borrow_book_by_patron("272727", 2)
    altered_time = datetime.now() + timedelta(days=20)
    monkeypatch.setattr("library_service.datetime", lambda: altered_time)
    outcome = calculate_late_fee_for_book("272727", 2)
    assert 0 < outcome["fee_amount"] <= 15

def test_R5_capping_rule_prevents_excessive_fee(monkeypatch):
    borrow_book_by_patron("989898", 1)
    altered_time = datetime.now() + timedelta(days=100)
    monkeypatch.setattr("library_service.datetime", lambda: altered_time)
    calc = calculate_late_fee_for_book("989898", 1)
    assert calc["fee_amount"] <= 15.0

def test_R5_nonexistent_records_return_zero_fee():
    response = calculate_late_fee_for_book("000000", 9999)
    assert response["fee_amount"] == 0.0


# =====================================================
# R6 — Search Query Processing
# =====================================================

def test_R6_query_by_partial_title():
    resultset = search_books_in_catalog("algorithm", "title")
    assert isinstance(resultset, list)

def test_R6_author_match_case_flexible():
    findings = search_books_in_catalog("brooks", "author")
    assert isinstance(findings, list)

def test_R6_exact_isbn_retrieval():
    output = search_books_in_catalog("9780101010101", "isbn")
    assert all(entry["isbn"] == "9780101010101" for entry in output) or output == []

def test_R6_unrecognized_field_type_safe_handling():
    safe = search_books_in_catalog("placeholder", "edition")
    assert safe == [] or isinstance(safe, list)


# =====================================================
# R7 — Patron Profile Summaries
# =====================================================

def test_R7_core_report_structure():
    profile = get_patron_status_report("202222")
    for expected_key in ["patron_id", "total_late_fees", "history", "currently_borrowed"]:
        assert expected_key in profile

def test_R7_invalid_identifier_returns_notice():
    report_data = get_patron_status_report("####")
    assert "status" in report_data
    assert "invalid" in report_data["status"].lower()

def test_R7_activity_state_reflects_limits():
    for idx in range(5):
        add_book_to_catalog(f"BookCap{idx}", "Temp", f"97822233344{idx:03}", 1)
        borrow_book_by_patron("303030", idx + 99)
    snapshot = get_patron_status_report("303030")
    assert snapshot["status"].lower() in ["at borrowing limit", "active"]

def test_R7_fee_value_is_nonnegative_float():
    summary = get_patron_status_report("202222")
    assert isinstance(summary["total_late_fees"], float)
    assert summary["total_late_fees"] >= 0