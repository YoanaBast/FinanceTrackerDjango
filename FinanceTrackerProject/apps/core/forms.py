# apps/core/forms.py
from django import forms
from .models import UserProfile, Income, Expense, Category, CURRENCY_CHOICES


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['default_currency', 'starting_amount']
        widgets = {
            'default_currency': forms.Select(),
            'starting_amount': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }


class BaseMoneyForm(forms.ModelForm):
    class Meta:
        widgets = {
            'amount': forms.NumberInput(attrs={'step': 0.01, 'min': 0}),
            'currency': forms.Select(choices=CURRENCY_CHOICES),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and not self.is_bound:
            profile = getattr(user, 'userprofile', None)
            if profile and 'currency' in self.fields:
                self.fields['currency'].initial = profile.default_currency

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class AddIncomeForm(BaseMoneyForm):
    class Meta(BaseMoneyForm.Meta):
        model = Income
        fields = ['category', 'amount', 'currency']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        # show only income categories
        self.fields['category'].queryset = Category.objects.filter(type='income')


class AddExpenseForm(BaseMoneyForm):
    class Meta(BaseMoneyForm.Meta):
        model = Expense
        fields = ['category', 'amount', 'currency']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        # include all expense categories, even if added dynamically
        self.fields['category'].queryset = Category.objects.filter(type='expense')

#
# class AddCategoryForm(forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = ['name']  # type will be set automatically
#         widgets = {
#             'name': forms.TextInput(attrs={'placeholder': 'New category'}),
#         }