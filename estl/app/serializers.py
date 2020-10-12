from rest_framework import serializers
from app.models import Employee

class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'eid',
            'login',
            'name',
            'salary',
        ]
