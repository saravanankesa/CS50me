import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Any
from wk8fnl.capstone.old.helper import (
    print_menu, process_expense_categories, process_income_categories,
    print_formatted_transaction, calculate_current_balance,
    calculate_summary_for_period
)

def initialize_db() -> None:
    """
    Initializes the database by creating a 'transactions' table if it doesn't already exist.
    This table stores all transaction data including type, category, name, amount, date, and pre-auth date.
    """
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def add_transaction() -> None:
    """
    Adds a new transaction to the database. Prompts the user to select the transaction type, category,
    and enter details such as name, amount, and date. Handles both expense and income transactions.
    """
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()

    transaction_types: List[str] = ['Expense', 'Income']
    expense_categories: Dict[str, List[str]] = {
        'General': ['Bills', 'Groceries', 'Rent', 'Fuel', 'Car Maintenance', 'Eating Out', 'Household', 'Fun'],
        'Pre-Auth Payments': ['Bills', 'Subscriptions']
    }
    income_categories: List[str] = ['CPP', 'OAS', 'GST', 'Email Money Transfers']

    print("\nSelect the type of transaction or enter '0' to return to the main menu:\n")
    for i, t_type in enumerate(transaction_types, start=1):
        print(f"{i}. {t_type}")
    type_input: str = input("\nEnter the number: ").strip()
    if type_input == '0':
        return
    try:
        type_selection: int = int(type_input)
        if not (1 <= type_selection <= len(transaction_types)):
            raise ValueError
        transaction_type: str = transaction_types[type_selection - 1]
    except ValueError:
        print("\nInvalid input Please enter a valid number from the list or '0' to return to the main menu.")
        return

    name: str = "N/A"  # Initialize name to "N/A"
    pre_auth_date: Optional[str] = None  # Initialize pre_auth_date to None

    # Handle expense categories
    if transaction_type == 'Expense':
        result = process_expense_categories(expense_categories)
        if result is None:  # Check if result is None, indicating invalid input or exit request
            print("Returning to makka menu.")
            return
        selected_expense_type, category = result
        if selected_expense_type == 'Pre-Auth Payments':
            pre_auth_date_input: str = input("Enter the Pre-Auth Payment date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(pre_auth_date_input, "%Y-%m-%d")
                pre_auth_date = pre_auth_date_input
            except ValueError:
                print("\nInvalid date format. Please enter the date in YYYY-MM-DD format.\n")
                return
        name = input("Enter the name of the expense: ").strip()

    # Handle income categories
    elif transaction_type == 'Income':
        result = process_income_categories(income_categories)
        if result is None:  # Check if result is None, indicating invalid input or exit request
            print("\nInvalid selection. Returning to kotta menu.")
            return
        category, name = result

    # Validate and convert amount input
    amount_input: str = input("Enter the amount: ").strip()
    try:
        amount: float = float(amount_input)
    except ValueError:
        print("\nInvalid amount. Please enter a valid number.\n")
        return

    datetime_now: str = datetime.now().strftime("%Y-%m-%d")  # Current date

    # Insert the transaction into the database
    cursor.execute('''INSERT INTO transactions (type, category, name, amount, datetime, pre_auth_date)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (transaction_type, category, name, amount, datetime_now, pre_auth_date))
    conn.commit()
    print("\nTransaction added successfully!\n")
    conn.close()

def add_transaction_refactored(conn: sqlite3.Connection, transaction_type: str, category: str, name: str, amount: float, pre_auth_date: Optional[str]) -> None:
    """
    A refactored version of add_transaction to directly insert a transaction into the database
    with given parameters.

    Parameters:
    - conn: Database connection object.
    - transaction_type: The type of transaction (Expense or Income).
    - category: The category of the transaction.
    - name: The name/description of the transaction.
    - amount: The monetary value of the transaction.
    - pre_auth_date: The date of a pre-authorized transaction, if applicable.
    """
    cursor = conn.cursor()
    datetime_now = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''INSERT INTO transactions (type, category, name, amount, datetime, pre_auth_date)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (transaction_type, category, name, amount, datetime_now, pre_auth_date))
    conn.commit()


def edit_transaction():
    """
    Prompts the user to edit an existing transaction. The user is asked to enter the ID of the
    transaction they wish to edit, and then provided with options to modify any of the transaction's
    details.
    """
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()

    # Display transactions for user selection
    list_transactions()

    # Ask for the ID of the transaction to edit
    transaction_id_str: str = input("\nEnter the ID of the transaction you wish to edit: ")
    try:
        transaction_id: int = int(transaction_id_str)
    except ValueError:
        print("\nInvalid transaction ID. Please enter a numeric value.\n")
        return

    # Retrieve the current values of the transaction
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction: Optional[Tuple] = cursor.fetchone()

    if transaction:
        print("\nCurrent values of the transaction:")
        print_formatted_transaction(transaction)

        # New values input
        new_type: str = input("Enter new type (Expense/Income) or press enter to keep current: ").capitalize() or transaction[1]
        new_category: str = input("Enter new category or press enter to keep current: ") or transaction[2]
        new_name: str = input("Enter new name or press enter to keep current: ") or transaction[3]
        new_amount_str: str = input("Enter new amount or press enter to keep current: ") or str(transaction[4])
        try:
            new_amount: float = float(new_amount_str)
        except ValueError:
            print("\nInvalid amount. Please enter a valid number.\n")
            return
        new_datetime: str = input("Enter new date (YYYY-MM-DD) or press enter to keep current: ") or transaction[5]
        new_pre_auth_date: str = input("Enter new pre-auth date (YYYY-MM-DD) or press enter to keep current: ") or transaction[6]

        # Update transaction in the database
        cursor.execute('''UPDATE transactions
                          SET type = ?, category = ?, name = ?, amount = ?, datetime = ?, pre_auth_date = ?
                          WHERE id = ?''',
                       (new_type, new_category, new_name, new_amount, new_datetime, new_pre_auth_date, transaction_id))

        conn.commit()
        print("\nTransaction updated successfully!\n")
    else:
        print("\nTransaction not found.\n")

    conn.close()

def edit_transaction_refactored(conn: sqlite3.Connection, transaction_id: int, new_values: dict) -> None:
    """
    Refactored version of edit_transaction to update an existing transaction in the database
    using the provided new values.

    Parameters:
    - conn: Database connection object.
    - transaction_id: The ID of the transaction to be updated.
    - new_values: A dictionary containing the transaction fields to be updated and their new values.
    """
    cursor = conn.cursor()
    # Construct the SQL update statement dynamically based on new_values
    fields = ", ".join([f"{key} = ?" for key in new_values.keys()])
    values = list(new_values.values()) + [transaction_id]
    cursor.execute(f'''UPDATE transactions SET {fields} WHERE id = ?''', values)
    conn.commit()



def delete_transaction() -> None:
    """
    Prompts the user to delete an existing transaction from the database. The user is asked
    to enter the ID of the transaction they wish to delete.
    """
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()

    list_transactions()  # Display transactions for user selection
    transaction_id_str: str = input("\nEnter the ID of the transaction to delete: ")
    try:
        transaction_id: int = int(transaction_id_str)
    except ValueError:
        print("\nInvalid transaction ID. Please enter a numeric value.\n")
        return

    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print("\nNo transaction found with the specified ID.\n")
    else:
        print("\nTransaction deleted successfully!\n")
    conn.close()


def list_transactions():
    """
    Retrieves and displays all transactions from the database in an ascending order by their IDs.
    """
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions ORDER BY id ASC')
    transactions: List[Tuple[Any, ...]] = cursor.fetchall()
    if transactions:
        print("\nList of Transactions:")
        for transaction in transactions:
            print_formatted_transaction(transaction)
    else:
        print("\nNo transactions found.\n")
    conn.close()

def upcoming_payments(conn: sqlite3.Connection) -> None:
    """
    Displays upcoming pre-authorized payments within the next 7 days.

    Parameters:
    - conn: Database connection object.
    """
    today: datetime = datetime.now()
    seven_days_later: datetime = today + timedelta(days=7)
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()

    # Format dates as strings in 'YYYY-MM-DD' format for the query
    cursor.execute('SELECT * FROM transactions WHERE type = "Expense" AND pre_auth_date BETWEEN ? AND ?',
                   (today.strftime('%Y-%m-%d'), seven_days_later.strftime('%Y-%m-%d')))
    upcoming_transactions: List[Tuple[Any, ...]] = cursor.fetchall()
    if upcoming_transactions:
        print("\nUpcoming Pre-Auth Payments within the next 7 days:")
        for transaction in upcoming_transactions:
            print_formatted_transaction(transaction)
    else:
        print("\nNo upcoming Pre-Auth payments within the next 7 days.\n")
    conn.close()

def calculate_balance() -> None:
    """
    Provides the user with options to view their current balance, and summary for the last 7, 30,
    or 90 days. The user selects an option to calculate and view the balance accordingly.
    """
    print("\nSelect an option to view balance:\n")
    print("1. Current Balance")
    print("2. Last 7 Days")
    print("3. Last 30 Days")
    print("4. Last 3 Months")
    choice: str = input("\nEnter your choice: ")
    if choice == '1':
        calculate_current_balance()
    elif choice == '2':
        calculate_summary_for_period(7)
    elif choice == '3':
        calculate_summary_for_period(30)
    elif choice == '4':
        calculate_summary_for_period(90)  # Approximation for 3 months
    else:
        print("\nInvalid choice. Please select a valid option.\n")


def main() -> None:
    """
    Main function to run the finance tracker program. Displays a welcome message upon first run
    and continuously prompts the user to choose from the main menu options until exit is selected.
    """
    welcome_msg = True   # Flag to check if program's first run
    initialize_db()   # Initialize database

    while True:
        if welcome_msg:
            print("\n********************")
            print("      WELCOME     ")
            print("         TO       ")
            print("     MONE~MOME    ")
            print("********************")
            welcome_msg = False  # Set flag to False after first run

        print_menu()
        choice: str = input("\nPick a menu number: ")
        if choice == '1':
            add_transaction()
        elif choice == '2':
            edit_transaction()
        elif choice == '3':
            delete_transaction()
        elif choice == '4':
            list_transactions()
        elif choice == '5':
            # Open a database connection before calling upcoming_payments
            conn = sqlite3.connect('transactions.db')
            try:
                upcoming_payments(conn)  # Pass the connection to the function
            finally:
                conn.close()  # Ensure the connection is closed after the function call
        elif choice == '6':
            calculate_balance()
        elif choice == '7':
            print("\n~~~Good-Bye~~~\n")
            break
        else:
            print("\nInvalid input! Please pick a number from the menu.")


if __name__ == "__main__":
    main()
