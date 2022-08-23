from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Sum
from .models import Expense
from categories.models import Category
from income.models import Income


@csrf_exempt
def index(request):
    if request.method == "POST":
        expense_item_id = request.POST.get("id")
        try:
            expense_item = Expense.objects.get(id=expense_item_id)
            expense_item.delete()
            message = f'Expense item with ID={expense_item_id} has been successfully deleted.'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=ok&msg_text={message}")
        except:
            message = f'Error during deleting the expense item with ID={expense_item_id}. The item has not been deleted.'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=error&msg_text={message}")
    else:
        expenses_list = Expense.objects.order_by('-expense_date')
        total_income = Income.objects.aggregate(Sum('amount'))['amount__sum']
        if not total_income:
            total_income = 0
        total_expenses = Expense.objects.aggregate(Sum('amount'))[
            'amount__sum']
        if not total_expenses:
            total_expenses = 0
        context = {
            'expenses_list': expenses_list,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance':  total_income - total_expenses,
            'msg_type': request.GET.get("msg_type"),
            'msg_text': request.GET.get("msg_text")
        }
        return render(request, 'expenses/index.html', context)


def add(request):
    if request.method == "POST":
        try:
            if request.POST.get('expense_category'):
                category = Category(id=request.POST.get('expense_category'))
            else:
                category = None
            new_expense_item = Expense(
                amount=request.POST.get('expense_amount'),
                expense_date=request.POST.get('expense_date'),
                category=category
            )
            new_expense_item.save()
            message = f'New expense item with ID={new_expense_item.id} has been added!'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=ok&msg_text={message}")
        except Exception as ex:
            message = f'Error during adding the data to the Expense table! {str(ex)}. New record has not been created!'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=error&msg_text={message}")
    else:
        categories_list = Category.objects.order_by('name')
        context = {
            'categories_list': categories_list,
            'form_type': "Creating",
            'form_url': "add"
        }
        return render(request, 'expenses/edit.html', context)


def edit(request, expense_id):
    expense_item = Expense.objects.filter(id=expense_id)
    categories_list = Category.objects.order_by('name')
    context = {
        'expense_item': expense_item,
        'categories_list': categories_list,
        'form_type': "Editing",
        'form_url': "edit"
    }
    return render(request, 'expenses/edit.html', context)


def save(request):
    if request.method == "POST":
        if request.POST.get('expense_category'):
            category = Category(id=request.POST.get('expense_category'))
        else:
            category = None
        try:
            expense_item = Expense.objects.get(
                id=request.POST.get("expense_id"))
            expense_item.amount = request.POST.get("expense_amount")
            expense_item.expense_date = request.POST.get("expense_date")
            expense_item.category = category
            expense_item.save()
            message = f'Expense item with ID={expense_item.id} has been successfully updated.'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=ok&msg_text={message}")
        except Exception as ex:
            message = f'Error! Expense item with ID={expense_item.id} has not been updated! {str(ex)}'
            return HttpResponseRedirect(f"/myfin/expenses/?msg_type=error&msg_text={message}")
