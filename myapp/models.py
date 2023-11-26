# myapp/models.py

from django.db import models
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.models import User

class Review(models.Model):
    content = models.TextField()
    ground_truth_annotation = models.IntegerField()  # 0, 1, or 2
    # ... other fields ...

class UnannotatedReview(models.Model):
    content = models.TextField()
    # You can add more fields as needed

class Annotation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)  # Assuming 'Review' is your review model
    value = models.IntegerField()  # Stores the annotation value




class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('dept1', 'Department 1'),
        ('dept2', 'Department 2'),
        # Add more departments as needed
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Ensure email is unique
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    program = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    password = models.CharField(max_length=128)
    accuracy = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # Hash password only if it's a new record or if the password has been changed
        if not self.pk or 'password' in kwargs.get('update_fields', []):
            self.password = make_password(self.password)
        super(Student, self).save(*args, **kwargs)


class StudentAnnotation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)
    annotation = models.TextField()  # or whatever field type is appropriate