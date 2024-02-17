import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from myapp.models import UnannotatedReview

def delete_reviews_with_three_or_more_annotations():
    # Filter UnannotatedReview objects with annotation_count >= 3
    reviews_to_delete = UnannotatedReview.objects.filter(annotation_count__gte=3)

    # Count reviews before deletion for reporting
    count_before = reviews_to_delete.count()

    # Delete the filtered reviews
    reviews_to_delete.delete()

    # Report the number of deleted reviews
    print(f"Deleted {count_before} reviews with 3 or more annotations.")

if __name__ == "__main__":
    delete_reviews_with_three_or_more_annotations()
