from django.shortcuts import render
from django.http.response import JsonResponse

from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from app.models import Employee
from app.serializers import EmployeeSerializer

@api_view(['GET'])
def employeeslist(request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        employees_serializer = EmployeeSerializer(employees, many=True)
        return JsonResponse(employees_serializer.data, safe=False)
