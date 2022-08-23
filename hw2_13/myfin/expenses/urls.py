from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('edit/<int:expense_id>/', views.edit, name='edit'),
    path('edit/', views.save, name='save')
]
