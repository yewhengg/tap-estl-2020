from django.urls import path, include
from app.views import dashboard, employeesinfo

urlpatterns = [
    path('', dashboard),
    path('users/', employeesinfo),
]
