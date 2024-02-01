from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview

class Command(BaseCommand):
    help = 'Delete all unannotated reviews from the database'

    def handle(self, *args, **options):
        UnannotatedReview.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all unannotated reviews.'))
