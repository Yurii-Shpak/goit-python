from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Sum
from .models import Income
from expenses.models import Expense


@csrf_exempt
def index(request):
    if request.method == "POST":
        income_item_id = request.POST.get("id")
        try:
            income_item = Income.objects.get(id=income_item_id)
            income_item.delete()
            message = f'Income item with ID={income_item_id} has been successfully deleted.'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=ok&msg_text={message}")
        except:
            message = f'Error during deleting the income item with ID={income_item_id}. The item has not been deleted.'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=error&msg_text={message}")
    else:
        income_list = Income.objects.order_by('-income_date')
        total_income = Income.objects.aggregate(Sum('amount'))['amount__sum']
        if not total_income:
            total_income = 0
        total_expenses = Expense.objects.aggregate(Sum('amount'))[
            'amount__sum']
        if not total_expenses:
            total_expenses = 0
        context = {
            'income_list': income_list,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance':  total_income - total_expenses,
            'msg_type': request.GET.get("msg_type"),
            'msg_text': request.GET.get("msg_text")
        }
        return render(request, 'income/index.html', context)


def edit(request, income_id):
    income_item = Income.objects.filter(id=income_id)
    context = {
        'income_item': income_item,
        'form_type': "Editing",
        'form_url': "edit"
    }
    return render(request, 'income/edit.html', context)


def save(request):
    if request.method == "POST":
        try:
            income_item = Income.objects.get(id=request.POST.get("income_id"))
            income_item.amount = request.POST.get("income_amount")
            income_item.income_date = request.POST.get("income_date")
            income_item.save()
            message = f'Income item with ID={income_item.id} has been successfully updated.'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=ok&msg_text={message}")
        except:
            message = f'Error! Income item with ID={income_item.id} has not been updated!'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=error&msg_text={message}")


def add(request):
    if request.method == "POST":
        try:
            new_income_item = Income(
                amount=request.POST.get('income_amount'),
                income_date=request.POST.get('income_date')
            )
            new_income_item.save()
            message = f'New income item with ID={new_income_item.id} has been added!'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=ok&msg_text={message}")
        except:
            message = 'Error during adding the data to the Income table! New record has not been created!'
            return HttpResponseRedirect(f"/myfin/income/?msg_type=error&msg_text={message}")
    else:
        return render(request, 'income/edit.html', {'form_type': "Creating", 'form_url': "add"})
