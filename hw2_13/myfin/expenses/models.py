from django.db import models
from datetime import date
from categories import models as categories_models


class Expense(models.Model):
    amount = models.FloatField(default=0)
    expense_date = models.DateField(default=date.today)
    category = models.ForeignKey(
        categories_models.Category, on_delete=models.SET_NULL, null=True)
