import requests
from django.db.models import Sum
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
    import requests
    converted = []
    for amt, frm in zip(amounts, from_currencies):
        if frm == to_currency:
            converted.append(amt)
            continue

        url = "http://127.0.0.1:8000/convert"
        params = {
            "amount": amt,
            "from_currency": frm,
            "to_currency": to_currency
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            converted.append(data.get("converted", amt))
        except Exception as e:
            print(f"Warning: {amt} {frm} -> {to_currency} failed: {e}")
            converted.append(amt)
        print(f"Request URL: {response.url}")
    return converted

