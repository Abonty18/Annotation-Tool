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
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

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
    annotation_count = models.IntegerField(default=0)  # New field to count annotations

class StudentAnnotation(models.Model):
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)

    # Student fields
    student1 = models.ForeignKey(CustomUser, related_name='student1_annotations', null=True, blank=True, on_delete=models.CASCADE)
    student2 = models.ForeignKey(CustomUser, related_name='student2_annotations', null=True, blank=True, on_delete=models.CASCADE)
    student3 = models.ForeignKey(CustomUser, related_name='student3_annotations', null=True, blank=True, on_delete=models.CASCADE)

    # Annotation fields
    student1annotation = models.IntegerField(null=True, blank=True)
    student2annotation = models.IntegerField(null=True, blank=True)
    student3annotation = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [('review', 'student1'), ('review', 'student2'), ('review', 'student3')]




class StudentProject(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    last_page = models.IntegerField(default=1)

class Annotation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='user_annotations')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='student_annotations')
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)
    value = models.IntegerField(null=True, blank=True)  # Stores the annotation value
    label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('review', 'student')



