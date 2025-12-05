from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import UserProfileForm, AddIncomeForm, AddExpenseForm
from .helpers import get_category_totals
from .models import UserProfile, CURRENCY_CHOICES

from django.db.models import Sum
from .models import Income, Expense, Category

from .helpers import convert_currency

@login_required
def dashboard(request):
    profile = getattr(request.user, 'userprofile', None)
    if not profile:
        return redirect("create_plan")

    # GET parameters
    target_currency = request.GET.get('currency', profile.default_currency)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Parse dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

    # Filter incomes/expenses for filtered period
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    if start_date:
        incomes = incomes.filter(created_at__gte=start_date)
        expenses = expenses.filter(created_at__gte=start_date)
    if end_date:
        incomes = incomes.filter(created_at__lt=end_date)
        expenses = expenses.filter(created_at__lt=end_date)

    # --- Filtered period conversion ---
    income_amounts = [i.amount for i in incomes]
    income_currencies = [i.currency for i in incomes]
    converted_incomes = convert_currency(income_amounts, income_currencies, target_currency)
    income_sum = round(sum(converted_incomes), 2)

    expense_amounts = [e.amount for e in expenses]
    expense_currencies = [e.currency for e in expenses]
    converted_expenses = convert_currency(expense_amounts, expense_currencies, target_currency)
    expenses_sum = round(sum(converted_expenses), 2)

    # --- All-time totals conversion ---
    all_incomes = Income.objects.filter(user=request.user)
    all_income_amounts = [i.amount for i in all_incomes]
    all_income_currencies = [i.currency for i in all_incomes]
    total_income = round(sum(convert_currency(all_income_amounts, all_income_currencies, target_currency)), 2)

    all_expenses = Expense.objects.filter(user=request.user)
    all_expense_amounts = [e.amount for e in all_expenses]
    all_expense_currencies = [e.currency for e in all_expenses]
    total_expenses = round(sum(convert_currency(all_expense_amounts, all_expense_currencies, target_currency)), 2)

    # Convert balance to target currency
    balance_converted = round(convert_currency([profile.balance], [profile.default_currency], target_currency)[0], 2)

    # Category totals (filtered period)
    category_expenses, category_incomes = get_category_totals(request.user, start_date, end_date)
    category_expenses = {k: round(convert_currency([v], [profile.default_currency], target_currency)[0], 2)
                         for k, v in category_expenses.items()}
    category_incomes = {k: round(convert_currency([v], [profile.default_currency], target_currency)[0], 2)
                        for k, v in category_incomes.items()}

    # Difference
    difference = {cat: category_incomes.get(cat, 0) - category_expenses.get(cat, 0)
                  for cat in set(category_incomes) | set(category_expenses)}
    difference = round(sum(difference.values()), 2)

    return render(request, "core/dashboard.html", {
        'balance': balance_converted,
        'income': income_sum,
        'expenses': expenses_sum,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'category_expenses': category_expenses,
        'category_incomes': category_incomes,
        'difference': difference,
        'currency': target_currency,
        'CURRENCY_CHOICES': CURRENCY_CHOICES
    })



@login_required
def create_plan(request):
    # Redirect if user already has a profile
    if hasattr(request.user, "userprofile"):
        return redirect("dashboard")

    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("dashboard")
    else:
        form = UserProfileForm()

    return render(request, "core/create_plan.html", {"form": form})

@login_required
def add_money(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        data = request.POST.copy()  # make a mutable copy
        if not data.get('currency'):  # default currency if none selected
            data['currency'] = profile.default_currency

        form = AddIncomeForm(data, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user

            # Convert to default currency if needed
            if income.currency != profile.default_currency:
                income.amount = convert_currency([income.amount], [income.currency], profile.default_currency)[0]
                income.currency = profile.default_currency

            income.save()
            profile.balance += income.amount
            profile.save()
            return redirect('dashboard')
    else:
        form = AddIncomeForm(user=request.user)  # unbound GET form

    return render(request, 'core/add_money.html', {'form': form})


@login_required
def subtract_money(request):
    profile = request.user.userprofile
    form = AddExpenseForm(user=request.user)

    if request.method == 'POST':
        data = request.POST.copy()
        if not data.get('currency'):
            data['currency'] = profile.default_currency

        form = AddExpenseForm(data, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user

            # Convert to default currency if needed
            if expense.currency != profile.default_currency:
                expense.amount = convert_currency([expense.amount], [expense.currency], profile.default_currency)[0]
                expense.currency = profile.default_currency

            expense.save()
            profile.balance -= expense.amount
            profile.save()
            return redirect('dashboard')
        else:
            print("Form errors:", form.errors)  # debug
    print("Expense form queryset:", form.fields['category'].queryset)

    return render(request, 'core/subtract_money.html', {'form': form})


@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        cat_type = request.POST.get("type")  # "income" or "expense"
        if not name or not cat_type:
            return JsonResponse({"success": False, "error": "Missing fields"})

        category, created = Category.objects.get_or_create(name=name, type=cat_type)
        return JsonResponse({"success": True, "id": category.id, "name": category.name})
    return JsonResponse({"success": False, "error": "Invalid request"})