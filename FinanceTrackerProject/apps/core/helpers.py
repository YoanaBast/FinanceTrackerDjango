import os
import requests
from django.db.models import Sum
from dotenv import load_dotenv
from .models import Income, Expense


def get_category_totals(user, start_date=None, end_date=None):
    filters = {'user': user}
    if start_date:
        filters['created_at__gte'] = start_date
    if end_date:
        filters['created_at__lte'] = end_date

    # Expenses
    category_expenses = (
        Expense.objects.filter(**filters)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .filter(total__gt=0)
    )
    category_expenses_dict = {item['category__name']: item['total'] for item in category_expenses}

    # Incomes
    category_incomes = (
        Income.objects.filter(**filters)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .filter(total__gt=0)
    )
    category_incomes_dict = {item['category__name']: item['total'] for item in category_incomes}

    return category_expenses_dict, category_incomes_dict



def convert_currency(amounts, from_currencies, to_currency):
    load_dotenv()
    API_KEY = os.environ.get("API_KEY")

    if len(amounts) != len(from_currencies):
        raise ValueError("Amounts and from_currencies must have the same length.")

    # Get all rates in one request
    unique_currencies = list(set(from_currencies + [to_currency]))
    url = "http://api.exchangerate.host/live"
    params = {
        "access_key": API_KEY,
        "source": to_currency,
        "currencies": ",".join(unique_currencies)
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        quotes = data.get("quotes", {})
    except Exception as e:
        print("Currency API error:", e)
        quotes = {}

    converted = []
    for amt, frm in zip(amounts, from_currencies):
        if frm == to_currency:
            converted.append(amt)
            continue
        # Rate from source to target
        key = f"{to_currency}{frm}"
        rate = quotes.get(key)
        if rate is None:
            print(f"Warning: rate for {frm} -> {to_currency} not found. Using 1.")
            rate = 1
        else:
            rate = 1 / rate  # invert because quotes are in TO->FROM format
        converted.append(amt * rate)

    return converted