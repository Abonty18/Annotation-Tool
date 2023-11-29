from django.core.management.base import BaseCommand
from myapp.models import Review
import json
import os

class Command(BaseCommand):
    help = 'Load a list of reviews from a JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('path', 'to', 'reviews.json')  # Update with correct path

        with open(file_path, 'r') as file:
            reviews = json.load(file)
            for review_data in reviews:
                Review.objects.get_or_create(
                    id=review_data['id'],
                    defaults={
                        'content': review_data['content'],
                        'ground_truth_annotation': review_data['label']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded reviews'))
