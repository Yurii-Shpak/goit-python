from django.urls import path

from income import views

urlpatterns = [
    path('', views.index, name='index'),
]
