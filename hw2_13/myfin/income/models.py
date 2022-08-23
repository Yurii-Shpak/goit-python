from django.db import models
from datetime import date


class Income(models.Model):
    amount = models.FloatField(default=0)
    income_date = models.DateField(default=date.today)
