from django.shortcuts import render
from django.db.models import Sum
from expenses.models import Expense
from income.models import Income
from categories.models import Category


def index(request):
    categories_list = Category.objects.order_by('name')

    if request.GET.get("from_date"):

        total_income = Income.objects.filter(
            income_date__range=[
                request.GET.get("from_date"),
                request.GET.get("to_date")]).aggregate(Sum('amount'))['amount__sum']
        if not total_income:
            total_income = 0

        total_expenses = Expense.objects.filter(
            expense_date__range=[
                request.GET.get("from_date"),
                request.GET.get("to_date")]).aggregate(Sum('amount'))['amount__sum']
        if not total_expenses:
            total_expenses = 0

        if request.GET.get("by_categories"):
            if request.GET.get("category") == '0':
                expenses_by_categories = Expense.objects.filter(
                    expense_date__range=[
                        request.GET.get("from_date"),
                        request.GET.get("to_date")]).values(
                    'category', 'category__name').annotate(category_amount=Sum('amount'))
            else:
                expenses_by_categories = Expense.objects.filter(
                    expense_date__range=[
                        request.GET.get("from_date"),
                        request.GET.get("to_date")],
                    category=request.GET.get("category")).values(
                    'category', 'category__name').annotate(category_amount=Sum('amount'))

            are_categories = len(
                expenses_by_categories) > 0 and request.GET.get("by_categories")
        else:
            are_categories = False
            expenses_by_categories = []

        context = {
            'is_report': True,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance':  total_income - total_expenses,
            'categories_list': categories_list,
            'expenses_by_categories': expenses_by_categories,
            'are_categories': are_categories
        }
    else:
        context = {'is_report': False, 'categories_list': categories_list}
    return render(request, 'report/index.html', context)
