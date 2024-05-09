from django.db import models
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Count, Case, When
from django.db import transaction

from django.utils import timezone
import datetime

from django.utils import timezone
import datetime
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
    annotation_count = models.IntegerField(default=0)
    # New fields
    DEPARTMENT_CHOICES = [
        ('cse', 'CSE'),
        ('eee', 'EEE'),
        ('mpe', 'MPE'),
        ('btm', 'BTM'),
        # ... other departments ...
    ]
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

    # has_taken_software_course = models.BooleanField(default=False)
    age = models.IntegerField(null=True, blank=True)
    working_experience = models.IntegerField(default=0)  # years of experience
    software_related_courses = models.JSONField(default=list)

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
    annotation_count = models.IntegerField(default=0)
    is_fully_annotated = models.BooleanField(default=False)

    def update_annotation_count(self):
        annotations = self.studentannotation_set.all()
        count = annotations.aggregate(
            total=Count(Case(When(student1annotation__isnull=False, then=1))) +
                  Count(Case(When(student2annotation__isnull=False, then=1))) +
                  Count(Case(When(student3annotation__isnull=False, then=1)))
        )['total']
        return count

    def save(self, *args, **kwargs):
        # Update the annotation count only if the instance is not new and it's not a partial update
        if not self._state.adding and 'update_fields' not in kwargs:
            updated_count = self.update_annotation_count()
            self.annotation_count = updated_count
            self.is_fully_annotated = (updated_count == 3)

        super().save(*args, **kwargs)






class ReviewLock(models.Model):
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE, related_name="locks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=True)
    lock_time = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.lock_time + datetime.timedelta(minutes=5)  # Lock expires after 5 minutes
    
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
     unique_together = [
        ('review', 'student1'),
        ('review', 'student2'),
        ('review', 'student3')
    ]

class StudentProject(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    last_page = models.IntegerField(default=1)
    uploaded_file = models.FileField(upload_to='uploads/%Y/%m/%d/')  # Define a FileField for file uploads


class Annotation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='user_annotations')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='student_annotations')
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)
    value = models.IntegerField(null=True, blank=True)  # Stores the annotation value
    label = models.CharField(max_length=100, null=True, blank=True)

# Add this model to your models.py file
class AnnotatedReview(models.Model):
    review = models.ForeignKey(UnannotatedReview, on_delete=models.CASCADE)
    content = models.TextField(default='')
    student1 = models.ForeignKey(CustomUser, related_name='student1_annotated_reviews', null=True, blank=True, on_delete=models.CASCADE)
    student2 = models.ForeignKey(CustomUser, related_name='student2_annotated_reviews', null=True, blank=True, on_delete=models.CASCADE)
    student3 = models.ForeignKey(CustomUser, related_name='student3_annotated_reviews', null=True, blank=True, on_delete=models.CASCADE)
    student1_annotation = models.IntegerField(null=True, blank=True)
    student2_annotation = models.IntegerField(null=True, blank=True)
    student3_annotation = models.IntegerField(null=True, blank=True)


@transaction.atomic
def move_annotated_reviews():
    unannotated_reviews = UnannotatedReview.objects.filter(is_fully_annotated=True)
    print(f"Starting to move reviews. Total to move: {unannotated_reviews.count()}")

    for review in unannotated_reviews:
        # Extract annotations
        annotations = list(review.studentannotation_set.all())
        if len(annotations) == 3:
            # Create the AnnotatedReview instance
            annotated_review, created = AnnotatedReview.objects.get_or_create(
                review=review,
                defaults={
                    'content': review.content,
                    'student1': annotations[0].student1,
                    'student1_annotation': annotations[0].student1annotation,
                    'student2': annotations[1].student2,
                    'student2_annotation': annotations[1].student2annotation,
                    'student3': annotations[2].student3,
                    'student3_annotation': annotations[2].student3annotation,
                }
            )
            if created:
                print(f"Created AnnotatedReview id {annotated_review.id} for UnannotatedReview id {review.id}")
            else:
                print(f"AnnotatedReview already exists for UnannotatedReview id {review.id}")
                

    print("Completed moving reviews.")


