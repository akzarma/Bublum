from django.db import models


# Create your models here.


class Vehicle(models.Model):
    number = models.CharField(max_length=15)
    mobile = models.PositiveIntegerField()
    address = models.CharField(max_length=250)
    type = models.CharField(max_length=100)


class Camera(models.Model):
    location = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class Violation(models.Model):
    description = models.CharField(max_length=200)
    fine_amount = models.CharField(max_length=100)


class VehicleViolation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

# class Config(models.Model):
#     graph_path =
