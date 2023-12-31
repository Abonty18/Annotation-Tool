from django.core.management.base import BaseCommand
from myapp.models import Review
import json

class Command(BaseCommand):
    help = 'Load a list of reviews from a JSON file'

    def handle(self, *args, **kwargs):
        # Path to your JSON file
        json_file_path = 'reviews.json'

        with open(json_file_path, 'r') as file:
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
