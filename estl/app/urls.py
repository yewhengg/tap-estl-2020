from django.urls import path, include
from app.views import dashboard, employeesinfo, uploadusers

urlpatterns = [
    path('', dashboard),
    path('users/', employeesinfo),
    path('users/upload', uploadusers),
]
