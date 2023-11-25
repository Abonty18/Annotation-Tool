# myapp/models.py

from django.db import models
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.models import User

class Review(models.Model):
    content = models.TextField()
    ground_truth_annotation = models.IntegerField()  # 0, 1, or 2
    # ... other fields ...


class Annotation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)  # Assuming 'Review' is your review model
    value = models.IntegerField()  # Stores the annotation value


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    DEPARTMENT_CHOICES = [
        ('dept1', 'Department 1'),
        ('dept2', 'Department 2'),
        # Add more departments as needed
    ]
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    program = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Student, self).save(*args, **kwargs)
