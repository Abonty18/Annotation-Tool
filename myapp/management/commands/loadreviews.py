# myapp/management/commands/loadreviews.py

from django.core.management.base import BaseCommand
from myapp.models import Review
import json

class Command(BaseCommand):
    help = 'Load a list of reviews from a JSON file'

    def handle(self, *args, **kwargs):
        with open('path/to/reviews.json', 'r') as file:
            reviews = json.load(file)
            for review_data in reviews:
                Review.objects.create(
                    id=review_data['id'],
                    content=review_data['content'],
                    ground_truth_annotation=review_data['label']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded reviews'))
