# myapp/models.py

from django.db import models
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # Hash the password before saving the user
        user.set_password(password)

        user.save(using=self._db)
        return user



class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    # New fields
    DEPARTMENT_CHOICES = [
        ('cse', 'CSE'),
        ('eee', 'EEE'),
        ('mpe', 'MPE'),
        ('btm', 'BTM'),
        # ... other departments ...
    ]
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='default_department_value')

    has_taken_software_course = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



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




class StudentAnnotation(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)
    annotation = models.TextField()  # or whatever field type is appropriate

class StudentProject(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    last_page = models.IntegerField(default=1)
