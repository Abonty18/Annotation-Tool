from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview, AnnotatedReview  # Adjust 'myapp' to your actual app name

class Command(BaseCommand):
    help = 'Moves reviews with exactly 3 annotations to AnnotatedReview and prints them'

    def handle(self, *args, **options):
        unannotated_reviews = UnannotatedReview.objects.filter(is_fully_annotated=True)
        self.stdout.write(f"Starting to move reviews. Total to move: {unannotated_reviews.count()}")

        for review in unannotated_reviews:
            annotations = review.studentannotation_set.all()
            if annotations.count() == 3:
                annotated_review, created = AnnotatedReview.objects.get_or_create(
                    review=review,
                    defaults={
                        'content': review.content,
                        'student1': annotations[0].student1,
                        'student2': annotations[1].student2,
                        'student3': annotations[2].student3,
                        'student1_annotation': annotations[0].student1annotation,
                        'student2_annotation': annotations[1].student2annotation,
                        'student3_annotation': annotations[2].student3annotation,
                    }
                )
                if created:
                    self.print_review_details(annotated_review)
                else:
                    self.stdout.write(f"AnnotatedReview already exists for UnannotatedReview ID {review.id}")

        self.stdout.write(self.style.SUCCESS("Completed moving and printing reviews."))

    def print_review_details(self, annotated_review):
        details = (
            f"Review ID: {annotated_review.review.id}\n"
            f"Content: {annotated_review.content}\n"
            f"Annotations: Student 1: {annotated_review.student1_annotation}, "
            f"Student 2: {annotated_review.student2_annotation}, "
            f"Student 3: {annotated_review.student3_annotation}\n"
        )
        self.stdout.write(details)
