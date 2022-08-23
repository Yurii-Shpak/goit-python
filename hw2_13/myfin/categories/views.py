from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Category


@csrf_exempt
def index(request):
    if request.method == "POST":
        category_id = request.POST.get("id")
        category_name = request.POST.get("name")
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            message = f'Category "{category_name}" with ID={category_id} has been successfully deleted.'
            return HttpResponseRedirect(f"/myfin/categories/?msg_type=ok&msg_text={message}")
        except:
            message = f'Error during deleting the category "{category_name}" with ID={category_id}. The category has not been deleted.'
            return HttpResponseRedirect(f"/myfin/categories/?msg_type=error&msg_text={message}")
    else:
        categories_list = Category.objects.order_by('name')
        context = {
            'categories_list': categories_list,
            'msg_type': request.GET.get("msg_type"),
            'msg_text': request.GET.get("msg_text")
        }
        return render(request, 'categories/index.html', context)


def add(request):
    if request.method == "POST":
        new_category_name = request.POST.get('category_name')
        if Category.objects.filter(name=new_category_name).count():
            message = f'Category "{new_category_name}" exists already! New record has not been created!'
            return HttpResponseRedirect(f"/myfin/categories/?msg_type=error&msg_text={message}")
        else:
            try:
                new_category = Category(name=new_category_name)
                new_category.save()
                message = f'New category with ID={new_category.id} has been added!'
                return HttpResponseRedirect(f"/myfin/categories/?msg_type=ok&msg_text={message}")
            except:
                message = 'Error during adding the data to the Category table! New record has not been created!'
                return HttpResponseRedirect(f"/myfin/categories/?msg_type=error&msg_text={message}")
    else:
        return render(request, 'categories/edit.html', {'form_type': "Creating", 'form_url': "add"})


def edit(request, category_id):
    category = Category.objects.filter(id=category_id)
    context = {
        'category': category,
        'form_type': "Editing",
        'form_url': "edit"
    }
    return render(request, 'categories/edit.html', context)


def save(request):
    if request.method == "POST":
        new_category_name = request.POST.get('category_name')
        if Category.objects.filter(name=new_category_name).exclude(id=request.POST.get('category_id')).count():
            message = f'Category "{new_category_name}" exists already! New record has not been updated!'
            return HttpResponseRedirect(f"/myfin/categories/?msg_type=error&msg_text={message}")
        else:
            try:
                category = Category.objects.get(
                    id=request.POST.get("category_id"))
                category.name = request.POST.get("category_name")
                category.save()
                message = f'Category "{category.name}" with ID={category.id} has been successfully updated.'
                return HttpResponseRedirect(f"/myfin/categories/?msg_type=ok&msg_text={message}")
            except:
                message = f'Error! Category with ID={category.id} has not been updated!'
                return HttpResponseRedirect(f"/myfin/categories/?msg_type=error&msg_text={message}")
