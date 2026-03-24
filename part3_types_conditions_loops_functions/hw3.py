#!/usr/bin/env python
from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

INCOME_QUERY_LENGTH = 3
COST_QUERY_LENGTH = 4
COST_CATEGORY_QUERY_LENGTH = 2
STATS_QUERY_LENGTH = 2
DATE_LENGTH = 10
DATE_FRAGMENTS_AMOUNT = 3
AMOUNT_OF_MONTHS = 12
FLOAT_FRAGMENTS = 2
DATE_SEPARATOR = "-"
DATE_SEP_FIRST_POS = 2
DATE_SEP_SECOND_POS = 5

DateTuple = tuple[int, int, int]
CategoryCosts = dict[str, float]
StatsResult = tuple[float, float, float, CategoryCosts]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    by_four = year % 4 == 0
    not_by_hundred = year % 100 != 0
    by_four_hundred = year % 400 == 0
    return (by_four and not_by_hundred) or by_four_hundred


def _has_valid_date_format(raw: str) -> bool:
    if len(raw) != DATE_LENGTH:
        return False
    first_ok = raw[DATE_SEP_FIRST_POS] == DATE_SEPARATOR
    second_ok = raw[DATE_SEP_SECOND_POS] == DATE_SEPARATOR
    return first_ok and second_ok


def _validate_day_month(day: int, month: int, year: int) -> bool:
    days_in_months = {
        1: 31, 2: 28, 3: 31, 4: 30,
        5: 31, 6: 30, 7: 31, 8: 31,
        9: 30, 10: 31, 11: 30, 12: 31,
    }
    if is_leap_year(year):
        days_in_months[2] = 29
    if month == 0 or month > AMOUNT_OF_MONTHS:
        return False
    return day != 0 and day <= days_in_months[month]


def extract_date(maybe_dt: str) -> DateTuple | None:
    if not _has_valid_date_format(maybe_dt):
        return None
    parts = maybe_dt.split(DATE_SEPARATOR)
    if len(parts) != DATE_FRAGMENTS_AMOUNT:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if not _validate_day_month(day, month, year):
        return None
    return day, month, year


def extract_valid_date(maybe_dt: str) -> DateTuple:
    parts = maybe_dt.split(DATE_SEPARATOR)

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    return day, month, year


def extract_amount(maybe_amount: str) -> float | None:
    sign = 1
    if maybe_amount[0] == "-":
        sign = -1
        maybe_amount = maybe_amount[1:]

    fragments = maybe_amount.replace(",", ".").split(".")
    if len(fragments) > FLOAT_FRAGMENTS:
        return None
    if len(fragments) == 0:
        return None
    for frag in fragments:
        if not frag.isdigit():
            return None
    joined = ".".join(fragments)
    return float(joined) * sign


def extract_category(raw: str) -> str | None:
    parts = raw.split("::")
    parent = parts[0]
    child = parts[1]
    if parent not in EXPENSE_CATEGORIES:
        return None
    if child not in EXPENSE_CATEGORIES[parent]:
        return None
    return child


def process_income(command: list[str]) -> None:
    if len(command) == INCOME_QUERY_LENGTH:
        _execute_income(command)
    else:
        print(UNKNOWN_COMMAND_MSG)


def _execute_income(command: list[str]) -> None:
    amount = extract_amount(command[1])
    date = extract_date(command[2])
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
    elif date is None:
        print(INCORRECT_DATE_MSG)
    else:
        print(income_handler(amount, command[2]))


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def process_cost(command: list[str]) -> None:
    cmd_len = len(command)
    is_categories_query = (
            cmd_len == COST_CATEGORY_QUERY_LENGTH
            and command[1] == "categories"
    )
    if is_categories_query:
        print(cost_categories_handler())
    elif cmd_len == COST_QUERY_LENGTH:
        _execute_cost(command)
    else:
        print(UNKNOWN_COMMAND_MSG)


def _execute_cost(command: list[str]) -> None:
    category_name = extract_category(command[1])
    amount = extract_amount(command[2])
    date = extract_date(command[3])
    if category_name is None:
        print(NOT_EXISTS_CATEGORY)
    elif amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
    elif date is None:
        print(INCORRECT_DATE_MSG)
    else:
        print(cost_handler(category_name, amount, command[3]))


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return str(EXPENSE_CATEGORIES)


def is_before(processing_date: str, report_date: str) -> bool:
    day, month, year = extract_date(report_date)
    proc_day, proc_month, proc_year = extract_date(processing_date)
    if proc_year < year:
        return True
    if proc_year != year:
        return False
    if proc_month < month:
        return True
    return month == proc_month and proc_day <= day


def is_within_month(processing_date: str, date: str) -> bool:
    same_month = extract_valid_date(processing_date)[1] == extract_valid_date(date)[1]
    same_year = extract_valid_date(processing_date)[2] == extract_valid_date(date)[2]
    return same_month and same_year


def _format_category_lines(category_costs: CategoryCosts) -> list[str]:
    lines = ["Details (category: amount):"]
    for idx, (name, amount) in enumerate(category_costs.items(), 1):
        lines.append(f"{idx}. {name}: {amount:.2f} rubles")
    return lines


def build_stats(stats: StatsResult, date: str) -> str:
    total, month_in, month_out, cat_costs = stats
    balance = month_in - month_out
    status = "loss" if balance < 0 else "profit"
    day, month, year = extract_date(date)

    lines = [
        f"Your statistics as of {day:0>2}-{month:0>2}-{year:0>4}:",
        f"Total capital: {total:.2f} rubles",
        f"This month, the {status} amounted to {balance:.2f} rubles.",
        f"Income: {month_in:.2f} rubles",
        f"Expenses: {month_out:.2f} rubles",
        "",
    ]
    lines.extend(_format_category_lines(cat_costs))
    lines.append("")
    return "\n".join(lines)


def process_stats(command: list[str]) -> None:
    if len(command) == STATS_QUERY_LENGTH:
        _execute_stats(command)
    else:
        print(UNKNOWN_COMMAND_MSG)


def _execute_stats(command: list[str]) -> None:
    date = extract_date(command[1])
    if date is None:
        print(INCORRECT_DATE_MSG)
    else:
        print(stats_handler(command[1]))


def stats_handler(report_date: str) -> str:
    total_amount = float(0)
    month_income = float(0)
    month_cost = float(0)
    category_costs: CategoryCosts = {}

    for transaction in financial_transactions_storage:
        proc_date = transaction["date"]
        if is_before(proc_date, report_date):
            if "category" in transaction:
                total_amount -= transaction["amount"]
                if is_within_month(proc_date, report_date):
                    month_cost += transaction["amount"]
                    category_costs.setdefault(transaction["category"], 0)
                    category_costs[transaction["category"]] += transaction["amount"]
            else:
                total_amount += transaction["amount"]
                if is_within_month(proc_date, report_date):
                    month_income += transaction["amount"]


    return build_stats((total_amount, month_income, month_cost, category_costs), report_date)


def handle_command(line: str) -> None:
    command = line.split(" ")
    if len(command) == 0:
        print(UNKNOWN_COMMAND_MSG)

    if command[0] == "income":
        process_income(command)
    elif command[0] == "cost":
        process_cost(command)
    elif command[0] == "stats":
        process_stats(command)
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    line = input()
    while line:
        if not line:
            continue
        handle_command(line)
        line = input()


if __name__ == "__main__":
    main()
