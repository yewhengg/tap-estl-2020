from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse

from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from http import HTTPStatus
import json
import pandas as pd
from io import StringIO

from app.models import Employee
from app.serializers import EmployeeSerializer

@api_view(['POST'])
def uploadusers(request):
    # check that request method is 'POST'
    # if not, return HTTP 400 Bad Request
    if request.method == 'POST':
        # check if its a HTTP multipart form, with csv data in form field "file"
        # with content-encoding "text/csv"
        # if not, return HTTP 400 Bad Request
        if "multipart/form-data" not in request.content_type:
            return JsonResponse({"status": "400", "message": "not HTTP multipart form"}, safe=False)
        if request.FILES['uploaded_file'].content_type != "text/csv":
            return JsonResponse({"status": "400", "message": "not text/csv content encoding"}, safe=False)
        # check success, processing CSV file
        file = request.FILES['uploaded_file']
        # check if csv is empty (no headers, no rows)
        # if not, parse data of csv into dataframe
        try:
            csv_df = pd.read_csv(StringIO(file.read().decode('UTF-8')), delimiter=',')
        except:
            return JsonResponse({"status": "400", "message": "empty csv with no headers and no data"}, safe=False)
        # check if number of columns is valid (== 4)
        if len(csv_df.columns) != 4:
            return JsonResponse({"status": "400", "message": "invalid number of columns"}, safe=False)
        # check if csv is empty (headers, no rows)
        if csv_df.empty:
            return JsonResponse({"status": "400", "message": "empty csv with headers but no data"}, safe=False)
        new_employees_obj = []
        for index, row in csv_df.iterrows():
            csv_eid = str(csv_df.at[index, 'eid'])
            # any row starting with # is considered a comment and ignored
            if csv_eid[0] == "#":
                continue
            csv_login = str(csv_df.at[index, 'login'])
            csv_name = str(csv_df.at[index, 'name'])
            # check if salary is a decimal
            try:
                csv_salary = float(csv_df.at[index, 'salary'])
            except:
                return JsonResponse({"status": "400", "message": "invalid salary data format, not a float"}, safe=False)
            # check if salary is < 0
            if csv_salary < 0.0:
                return JsonResponse({"status": "400", "message": "invalid salary data, less than 0"}, safe=False)
            # check if eid exist in the database
            # update login, name, salary if eid exist
            # else add new employee
            if Employee.objects.filter(eid__icontains = csv_eid).exists():
                # check if new login to be updated exist in the database
                # assuming in database, there exist
                # EmployeeA(eid=1, login=A, name=B, salary=C)
                # EmployeeB(eid=2, login=D, name=E, salary=F)
                # csv row is (eid=1, login=D, name=X, salary=Y)
                # after updating
                # EmployeeA(eid=1, login=D, name=X, salary=Y)
                # EmployeeB(eid=2, login=A, name=E, salary=F)
                if Employee.objects.filter(login__icontains = csv_login).exists():
                    temp_employee_one = Employee.objects.filter(eid__icontains = csv_eid).first()
                    temp_employee_two = Employee.objects.filter(login__icontains = csv_login).first()
                    temp_login_one = temp_employee_one.login
                    temp_eid_two = temp_employee_two.eid
                    Employee.objects.filter(eid__icontains = csv_eid).\
                        update(
                            login = "thisissomearbitraryandtemporarylogin"
                        )
                    Employee.objects.filter(eid__icontains = temp_eid_two).\
                        update(
                            login = temp_login_one
                        )
                    Employee.objects.filter(eid__icontains = csv_eid).\
                        update(
                            login = csv_login,
                            name = csv_name,
                            salary = csv_salary
                        )
                else:
                    Employee.objects.filter(eid__icontains = csv_eid).\
                        update(
                            login = csv_login,
                            name = csv_name,
                            salary = csv_salary
                        )
            else:
                new_employees_obj.append(
                    Employee(
                        eid = csv_eid,
                        login = csv_login,
                        name = csv_name,
                        salary = csv_salary
                    )
                )
        try:
            new_employees_bulkcreate = Employee.objects.bulk_create(new_employees_obj)
            return JsonResponse({"status": "200", "message": "success"}, safe=False)
        except:
            return JsonResponse({"status": "400", "message": "unable to add data into database"}, safe=False)
    else:
        return JsonResponse({"status": "405", "message": "method not allowed. POST only"}, safe=False)

@api_view(['GET'])
def dashboard(request):
    # check that request method is 'GET'
    # if not, return HTTP 400 Bad Request
    if request.method == 'GET':
        employees = Employee.objects.all()[:30]
        employees_serializer = EmployeeSerializer(employees, many=True)
        context = {"result": employees_serializer.data}
        return render(request, 'index.html', {"result": context.items()})
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
        # check success, extracting data from database
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
