from django.core.management.base import BaseCommand
from django.db.models import Count, Case, When
from django.core.paginator import Paginator
from myapp.models import UnannotatedReview, StudentAnnotation

class Command(BaseCommand):
    help = 'Corrects the annotation counts for UnannotatedReview instances starting from a specific ID.'

    def add_arguments(self, parser):
        parser.add_argument('--start-id', type=int, help='ID of the review to start processing from', default=0)

    def handle(self, *args, **options):
        start_id = options['start_id']
        self.stdout.write(f"Starting to correct annotation counts for reviews with ID greater than {start_id}...")

        reviews_to_correct = UnannotatedReview.objects.filter(id__gt=start_id).order_by('id')
        paginator = Paginator(reviews_to_correct, 100)  # Adjust batch size as needed

        fully_annotated_count = 0
        corrected_count = 0
        processed_count = 0

        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            for review in page.object_list:
                try:
                    self.stdout.write(f"Processing review ID {review.id}...")
                    annotations = StudentAnnotation.objects.filter(review=review)
                    actual_count = annotations.aggregate(
                        count=Count(Case(When(student1annotation__isnull=False, then=1))) +
                              Count(Case(When(student2annotation__isnull=False, then=1))) +
                              Count(Case(When(student3annotation__isnull=False, then=1)))
                    )['count']

                    if review.annotation_count != actual_count:
                        review.annotation_count = actual_count
                        review.save()
                        self.stdout.write(f"Corrected review {review.id} to have {actual_count} annotations.")
                        corrected_count += 1

                    if actual_count == 3:
                        fully_annotated_count += 1

                    processed_count += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating review {review.id}: {e}"))

            self.stdout.write(f"Completed processing page {page_num} of {paginator.num_pages}.")

        self.stdout.write(self.style.SUCCESS(f"Completed correcting annotation counts. {corrected_count} reviews corrected, with {fully_annotated_count} fully annotated. Processed {processed_count} reviews in total."))
