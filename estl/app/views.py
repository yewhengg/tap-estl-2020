from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse

from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from http import HTTPStatus
import json

from app.models import Employee
from app.serializers import EmployeeSerializer

@api_view(['GET'])
def dashboard(request):
    # check that request method is 'GET'
    # if not, return HTTP 400 Bad Request
    if request.method == 'GET':
        employees = Employee.objects.all()[:30]
        employees_serializer = EmployeeSerializer(employees, many=True)
        context = {"result": employees_serializer.data}
        return render(request, 'index.html', {"result": context.items()})
        # return JsonResponse({"Hello": "World"}, safe=False)
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

@api_view(['GET'])
def employeesinfo(request):
    # check that request method is 'GET'
    # if not, return HTTP 400 Bad Request
    if request.method == 'GET':
        # check if there are any missing request params or invalid request params data format
        # if any, return HTTP 400 Bad Request
        try:
            request_minsalary = float(request.GET["minSalary"])
            request_maxsalary = float(request.GET["maxSalary"])
            request_offset = int(request.GET["offset"])
            request_limit = int(request.GET["limit"])
            request_sort = str(request.GET["sort"])
        except:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        # check if there are any invalid logic for request params
        # if any, return HTTP 400 Bad Request
        if request_minsalary < 0:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_maxsalary < 0:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_minsalary > request_maxsalary:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_offset < 0:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_limit < 0:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_sort[0] != "+" and request_sort[0] != "-":
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        if request_sort[1:] != "eid" and request_sort[1:] != "login" and request_sort[1:] != "name" and request_sort[1:] != "salary":
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        # success, extracting data from database
        if request_sort[0] == "+":
            employees = Employee.objects.all().\
                filter(salary__gte = request_minsalary).\
                filter(salary__lte = request_maxsalary).\
                order_by(request_sort[1:])[request_offset:int(request_offset + request_limit)]
        if request_sort[0] == "-":
            employees = Employee.objects.all().\
                filter(salary__gte = request_minsalary).\
                filter(salary__lte = request_maxsalary).\
                order_by(request_sort)[request_offset:int(request_offset + request_limit)]
        employees_serializer = EmployeeSerializer(employees, many=True)
        context = {"result": employees_serializer.data}
        try:
            if request.headers['User-Agent']:
                return render(request, 'index.html', {"result": context.items()})
        except:
            return JsonResponse(context, safe=False)
    else:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
