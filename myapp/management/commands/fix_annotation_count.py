from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview, StudentAnnotation

class Command(BaseCommand):
    help = 'Updates the annotation counts for the first 100 UnannotatedReview based on filled annotation fields in StudentAnnotation.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to update annotation counts for the first 100 reviews...'))
        
        # Iterate over the first 100 reviews, you might want to order them by a specific field
        for review in UnannotatedReview.objects.all().order_by('id')[15000:21712]:
            # Fetch all annotations related to the current review
            annotations = StudentAnnotation.objects.filter(review=review)
            
            # Initialize the count for the current review
            annotation_count = 0
            
            # Iterate over each annotation entry to check filled annotation fields
            for annotation in annotations:
                if annotation.student1annotation is not None:
                    annotation_count += 1
                if annotation.student2annotation is not None:
                    annotation_count += 1
                if annotation.student3annotation is not None:
                    annotation_count += 1
            
            # Update the review's annotation count if it's different
            if review.annotation_count != annotation_count:
                review.annotation_count = annotation_count
                review.save()
                self.stdout.write(self.style.SUCCESS(f'Updated review {review.id} with new annotation count: {annotation_count}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated annotation counts for the first 100 reviews.'))
