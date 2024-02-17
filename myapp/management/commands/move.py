from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import UnannotatedReview, AnnotatedReview, StudentAnnotation

class Command(BaseCommand):
    help = 'Move fully annotated reviews from UnannotatedReview to AnnotatedReview.'

    def handle(self, *args, **options):
        # Filter for reviews that are fully annotated
        fully_annotated_reviews = UnannotatedReview.objects.filter(annotation_count=3)

        with transaction.atomic():
            for review in fully_annotated_reviews:
                # Assuming StudentAnnotation links to UnannotatedReview via a ForeignKey
                annotations = StudentAnnotation.objects.filter(review=review)
                
                if annotations.count() == 3:  # Double-check to ensure there are exactly 3 annotations
                    # Create a new AnnotatedReview instance with data from UnannotatedReview and annotations
                    AnnotatedReview.objects.create(
                        review=review,
                        content=review.content,
                        student1=annotations[0].student1,
                        student2=annotations[1].student2,
                        student3=annotations[2].student3,
                        student1_annotation=annotations[0].student1annotation,
                        student2_annotation=annotations[1].student2annotation,
                        student3_annotation=annotations[2].student3annotation,
                    )
                    
                    # Optionally, delete the original UnannotatedReview and related annotations if no longer needed
                    # review.delete()

            self.stdout.write(self.style.SUCCESS(f'Successfully moved {fully_annotated_reviews.count()} reviews to AnnotatedReview.'))
