from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
import pycountry

# Create your models here.

CURRENCY_CHOICES = sorted(
    [(c.alpha_3, c.name) for c in pycountry.currencies],
    key=lambda x: x[1]
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    starting_amount = models.FloatField(validators=[MinValueValidator(0)])
    balance = models.FloatField(default=0)  # will set to starting_amount initially

    def save(self, *args, **kwargs):
        if not self.pk:  # only for new profiles
            self.balance = self.starting_amount
        super().save(*args, **kwargs)

class Category(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    name = models.CharField(unique=True)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'type')

class Money(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)  # auto timestamp

    def save(self, *args, **kwargs):
        if not self.currency and hasattr(self.user, 'userprofile'):
            self.currency = self.user.userprofile.default_currency
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class Income(Money):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')


class Expense(Money):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
