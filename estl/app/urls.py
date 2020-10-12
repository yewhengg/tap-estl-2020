from django.urls import path, include
from app.views import employeeslist

urlpatterns = [
    path('', employeeslist)
]
