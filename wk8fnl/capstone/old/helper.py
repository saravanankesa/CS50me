from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
import sqlite3

def print_menu():
    print("\n~~~~~~~~Menu~~~~~~~~")
    print("1. Add Transaction")
    print("2. Edit Transaction")
    print("3. Delete Transaction")
    print("4. List Transactions")
    print("5. Upcoming Payments")
    print("6. Calculate Balances")
    print("7. Exit")



def process_expense_categories(expense_categories: Dict[str, list[str]]) -> Optional[Tuple[str, str]]:
    print("\nSelect the type of expense:")
    for i, expense_type in enumerate(expense_categories.keys(), start=1):
        print(f"{i}. {expense_type}")
    expense_type_input: str = input("\nEnter the number for the expense type: ").strip()
    if expense_type_input == '0': return None
    try:
        selected_expense_type: str = list(expense_categories.keys())[int(expense_type_input) - 1]
    except (ValueError, IndexError):
        print("Invalid selection. Returning to main menu.")
        return None
    print("\nSelect the expense category:")
    for i, category in enumerate(expense_categories[selected_expense_type], start=1):
        print(f"{i}. {category}")
    category_input: str = input("\nEnter the number for the category: ").strip()
    if category_input == '0': return None
    try:
        category: str = expense_categories[selected_expense_type][int(category_input) - 1]
    except (ValueError, IndexError):
        print("Invalid selection. Returning to main menu.")
        return None
    return selected_expense_type, category


def process_income_categories(income_categories: List[str]) -> Optional[Tuple[str, str]]:
    print("\nSelect the income category:")
    for i, category in enumerate(income_categories, start=1):
        print(f"{i}. {category}")
    category_input: str = input("\nEnter the number for the category: ").strip()
    if category_input == '0': return None
    try:
        category: str = income_categories[int(category_input) - 1]
        product_name: str = "N/A"  # Default value
        if category == 'Email Money Transfers':
            product_name = input("Enter the name of the Email Money Transfer sender: ").strip()
    except (ValueError, IndexError):
        print("Invalid selection. Returning to main menu.")
        return None
    return category, product_name

def print_formatted_transaction(transaction):
    id, transaction_type, category, name, amount, datetime_str, pre_auth_date = transaction
    pre_auth_date_display = pre_auth_date if pre_auth_date else 'N/A'
    print(f"{id}. Type: {transaction_type}, Category: {category}, Name: {name}, "
          f"Amount: ${amount:.2f}, Date: {datetime_str}, Pre-Auth Date: {pre_auth_date_display}")


def calculate_current_balance() -> None:
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()
    # Calculate Total Income
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Income'")
    total_income: float = cursor.fetchone()[0] or 0.0
    # Calculate Total Expenses (excluding upcoming pre-auth payments)
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND (pre_auth_date IS NULL OR pre_auth_date <= ?)", (datetime.now().strftime('%Y-%m-%d'),))
    total_expenses: float = cursor.fetchone()[0] or 0.0
    # Print Current Balance
    print(f"\nCurrent Balance:\nTotal Income: ${total_income:.2f}\nTotal Expenses: ${total_expenses:.2f}\nBalance: ${total_income - total_expenses:.2f}")
    conn.close()

def calculate_summary_for_period(days: int) -> None:
    start_date: datetime = datetime.now() - timedelta(days=days)
    conn: sqlite3.Connection = sqlite3.connect('transactions.db')
    cursor: sqlite3.Cursor = conn.cursor()
    # Calculate Total Income for the period
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND datetime >= ?", (start_date.strftime('%Y-%m-%d'),))
    total_income: float = cursor.fetchone()[0] or 0.0
    # Calculate Total Expenses for the period (excluding future pre-auth payments)
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND datetime >= ? AND (pre_auth_date IS NULL OR pre_auth_date <= ?)", (start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
    total_expenses: float = cursor.fetchone()[0] or 0.0
    # Calculate Total Pre-Auth Payments made within the period
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND pre_auth_date >= ? AND pre_auth_date <= ?", (start_date.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
    total_pre_auth_payments: float = cursor.fetchone()[0] or 0.0
    # Print Summary
    print(f"\nSummary for the last {days} days:")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expenses (excluding upcoming pre-auth payments): ${total_expenses:.2f}")
    print(f"Total Pre-Auth Payments (paid): ${total_pre_auth_payments:.2f}")
    print(f"Final Balance: ${total_income - total_expenses:.2f}")
    conn.close()
