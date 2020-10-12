from django.db import models

class Employee(models.Model):
    class Meta:
        db_table = 'employees'
    eid = models.CharField(max_length=255, null=False, unique=True, blank=False, default='')
    login = models.CharField(max_length=255, null=False, unique=True, blank=False, default='')
    name = models.CharField(max_length=255, null=False, blank=False, default='')
    salary = models.DecimalField(max_digits=10, decimal_places=3, null=False, blank=False, default='')
