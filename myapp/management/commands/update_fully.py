from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview  # Adjust 'myapp' to your actual app name

class Command(BaseCommand):
    help = 'Updates the is_fully_annotated field for reviews with 3 annotations'

    def handle(self, *args, **options):
        reviews_to_update = UnannotatedReview.objects.filter(annotation_count=3)
        count = reviews_to_update.update(is_fully_annotated=True)
        self.stdout.write(self.style.SUCCESS(f'Updated {count} reviews to be marked as fully annotated.'))
