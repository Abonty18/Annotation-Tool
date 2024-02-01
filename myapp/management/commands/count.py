from django.core.management.base import BaseCommand
from myapp.models import CustomUser, StudentAnnotation
from django.db.models import Q


class Command(BaseCommand):
    help = 'Initializes annotation counts for existing users'

    def handle(self, *args, **kwargs):
        for user in CustomUser.objects.all():
            count = StudentAnnotation.objects.filter(
                Q(student1=user) | Q(student2=user) | Q(student3=user)
            ).distinct().count()
            
            user.annotation_count = count
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated count for {user.email} to {count}'))
