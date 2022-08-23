from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/<int:income_id>/', views.edit, name='edit'),
    path('edit/', views.save, name='save'),
    path('add/', views.add, name='add')
]
