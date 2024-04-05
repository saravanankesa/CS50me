import pytest
import sqlite3
from datetime import datetime, timedelta
from project import initialize_db, add_transaction_refactored, edit_transaction_refactored, upcoming_payments
from helper import process_expense_categories, process_income_categories, calculate_current_balance, calculate_summary_for_period
from unittest.mock import MagicMock, patch

@pytest.fixture
def db():
    """Fixture to setup a test database and tear it down after tests."""
    # Setup: create a new in-memory database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    # Create table rows
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            datetime DATE NOT NULL,
            pre_auth_date DATE
        )
    ''')
    # Yield the connection and cursor to the test
    yield conn
    # Teardown: close the connection after the test is done
    conn.close()

def test_initialize_db(db):
    """Test that the database initializes correctly using pytest."""
    conn = db  # Unpack the db fixture to get the connection and cursor if needed
    # Create a cursor object using the connection
    cursor = conn.cursor()
    # Call the function to test
    initialize_db()
    # Now check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
    table_exists = cursor.fetchone()
    assert table_exists is not None, "The transactions table should be created."

def add_dummy_transaction(conn):
    """Helper function to add a dummy transaction for testing."""
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO transactions (type, category, name, amount, datetime, pre_auth_date)
                      VALUES ('Income', 'Salary', 'Test', 1000, '2023-01-01', NULL)''')
    conn.commit()
    return cursor.lastrowid

def test_add_transaction(db):
    """Test adding a transaction."""
    # Example transaction data
    transaction_type = 'Income'
    category = 'Salary'
    name = 'Monthly Salary'
    amount = 5000.00
    pre_auth_date = None

    add_transaction_refactored(db, transaction_type, category, name, amount, pre_auth_date)

    # Verify the transaction was added
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions WHERE name = ?", (name,))
    transaction = cursor.fetchone()

    assert transaction is not None, "Transaction should be added to the database."
    assert transaction[1] == transaction_type
    assert transaction[2] == category
    assert transaction[3] == name
    assert transaction[4] == amount


def test_edit_transaction(db):
    """Test editing a transaction."""
    transaction_id = add_dummy_transaction(db)

    new_values = {
        'type': 'Expense',
        'category': 'Utilities',
        'name': 'Electricity Bill',
        'amount': 150,
        'datetime': '2023-01-02',
        # Assume pre_auth_date remains unchanged or NULL
    }

    edit_transaction_refactored(db, transaction_id, new_values)

    # Verify the transaction was updated
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()

    assert transaction, "Transaction should exist."
    assert transaction[1] == new_values['type'], "Type should be updated."
    assert transaction[2] == new_values['category'], "Category should be updated."
    assert transaction[3] == new_values['name'], "Name should be updated."
    assert transaction[4] == new_values['amount'], "Amount should be updated."
    assert transaction[5] == new_values['datetime'], "Datetime should be updated."


def add_payment(conn, type, category, amount, pre_auth_date):
    """Helper function to add a payment for testing."""
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO transactions (type, category, name, amount, datetime, pre_auth_date)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (type, category, "Test Payment", amount, datetime.now().strftime('%Y-%m-%d'), pre_auth_date))
    conn.commit()

def test_upcoming_payments_no_payments(db):
    """Test that no upcoming payments are found when none are scheduled."""
    # Assume no pre-auth payments are added
    upcoming_payments(db)  # You may need to capture stdout to assert on printed output

    # Check output/assert here based on how upcoming_payments is implemented
    # This step will vary based on your setup

def test_upcoming_payments_with_payments(db):
    """Test that upcoming pre-auth payments are correctly identified."""
    add_payment(db, "Expense", "Bills", 100, (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'))
    add_payment(db, "Expense", "Bills", 200, (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d'))  # Outside 7 days window

@pytest.mark.parametrize("user_inputs,expected", [
    (["1", "1"], ("General", "Bills")),  # Test selecting the first option in both prompts
    (["2", "1"], ("Pre-Auth Payments", "Bills")),  # Test selecting the second option, then the first
    (["0"], None),  # Test exiting on the first prompt
    (["1", "0"], None),  # Test exiting on the second prompt
    (["3"], None),  # Test invalid option in the first prompt
    (["1", "10"], None),  # Test invalid option in the second prompt
])
def test_process_expense_categories(user_inputs, expected):
    expense_categories = {
        "General": ["Bills", "Groceries"],
        "Pre-Auth Payments": ["Bills", "Subscriptions"]
    }

    with patch('builtins.input', side_effect=user_inputs), patch('builtins.print') as mock_print:
        result = process_expense_categories(expense_categories)
        assert result == expected

@pytest.mark.parametrize("user_inputs,expected", [
    (["1"], ("CPP", "N/A")),  # Test selecting the first option with default product name
    (["2"], ("OAS", "N/A")),  # Test selecting the second option with default product name
    (["4", "John Doe"], ("Email Money Transfers", "John Doe")),  # Test Email Money Transfer with a specified name
    (["0"], None),  # Test exiting
    (["5"], None),  # Test invalid option
])
def test_process_income_categories(user_inputs, expected):
    income_categories = ["CPP", "OAS", "GST", "Email Money Transfers"]

    with patch('builtins.input', side_effect=user_inputs), patch('builtins.print') as mock_print:
        result = process_income_categories(income_categories)
        assert result == expected

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database connection and cursor."""
    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_conn.cursor.return_value = mock_cursor

    # Mock the fetchone response for income and expenses
    mock_cursor.fetchone.side_effect = [
        (1000,),  # Total income
        (500,),   # Total expenses
    ]

    # Replace the sqlite3.connect with our mock connection
    monkeypatch.setattr(sqlite3, 'connect', lambda _: mock_conn)
    return mock_conn, mock_cursor

def test_calculate_current_balance(mock_db, capsys):
    """Test the calculate_current_balance function."""
    _, mock_cursor = mock_db
    calculate_current_balance()
    captured = capsys.readouterr()

    # Verify the correct SQL queries were executed
    mock_cursor.execute.assert_any_call("SELECT SUM(amount) FROM transactions WHERE type = 'Income'")
    mock_cursor.execute.assert_any_call("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND (pre_auth_date IS NULL OR pre_auth_date <= ?)", (datetime.now().strftime('%Y-%m-%d'),))

    # Verify the output
    assert "Current Balance:\nTotal Income: $1000.00\nTotal Expenses: $700.00\nBalance: $300.00" in captured.out

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database connection and cursor."""
    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_conn.cursor.return_value = mock_cursor

    # Mock the fetchone response for income, expenses, and pre-auth payments
    mock_cursor.fetchone.side_effect = [
        (1000,),  # Total income
        (700,),   # Total expenses
        (300,),   # Total pre-auth payments
    ]

    # Replace the sqlite3.connect with our mock connection
    monkeypatch.setattr(sqlite3, 'connect', lambda _: mock_conn)
    return mock_conn, mock_cursor

def test_calculate_summary_for_period(mock_db, capsys):
    """Test the calculate_summary_for_period function."""
    _, mock_cursor = mock_db
    days = 30
    calculate_summary_for_period(days)
    captured = capsys.readouterr()

    # Verify the correct SQL queries were executed with correct parameters
    start_date = datetime.now() - timedelta(days=days)
    mock_cursor.execute.assert_any_call("SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND datetime >= ?", (start_date.strftime('%Y-%m-%d'),))
    mock_cursor.execute.assert_any_call("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND datetime >= ? AND (pre_auth_date IS NULL OR pre_auth_date <= ?)", (start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
    mock_cursor.execute.assert_any_call("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND pre_auth_date >= ? AND pre_auth_date <= ?", (start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))

    # Verify the output
    assert f"\nSummary for the last {days} days:" in captured.out
    assert "Total Income: $1000.00" in captured.out
    assert "Total Expenses (excluding upcoming pre-auth payments): $700.00" in captured.out
    assert "Total Pre-Auth Payments (paid): $300.00" in captured.out
    assert "Final Balance: $300.00" in captured.out



def teardown_test_db(conn):
    conn.close()

# Main function to run tests
if __name__ == "__main__":
    test_initialize_db(db)
