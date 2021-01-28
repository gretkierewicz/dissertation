from django.db import models

from modules.models import Classes


class Orders(models.Model):
    classes = models.OneToOneField(Classes, on_delete=models.CASCADE)
    students_number = models.IntegerField()
    order_number = models.CharField(max_length=50, blank=True, null=True)
