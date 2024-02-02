# signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from myapp.models import StudentAnnotation, CustomUser, UnannotatedReview
from django.db.models import Count

@receiver(post_save, sender=StudentAnnotation)
@receiver(post_delete, sender=StudentAnnotation)
def update_annotation_counts(sender, instance, **kwargs):
    # Update UnannotatedReview annotation count
    review = instance.review
    review.annotation_count = StudentAnnotation.objects.filter(review=review).count()
    review.save()

    # Assuming each StudentAnnotation has one student related to it. Adjust according to your model.
    # Update CustomUser annotation count
    students = [instance.student1, instance.student2, instance.student3]
    for student in students:
        if student:
            student.annotation_count = StudentAnnotation.objects.filter(
                student1=student
            ).count()
            student.save()
