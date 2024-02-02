from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from myapp.models import StudentAnnotation, CustomUser
from django.db.models import Q


@receiver(post_save, sender=StudentAnnotation)
@receiver(post_delete, sender=StudentAnnotation)
def update_annotation_count(sender, instance, **kwargs):
    # Iterate over all users related to the annotation and update their count
    for user in [instance.student1, instance.student2, instance.student3]:
        if user is not None:
            user.annotation_count = StudentAnnotation.objects.filter(
                Q(student1=user) | Q(student2=user) | Q(student3=user)
            ).distinct().count()
            user.save()
