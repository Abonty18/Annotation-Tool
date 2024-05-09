from myapp.models import UnannotatedReview

def count_reviews_by_annotation_count():
    # Count reviews with annotation count 3
    count_annotation_3 = UnannotatedReview.objects.filter(annotation_count=3).count()

    # Count reviews with annotation count 2
    count_annotation_2 = UnannotatedReview.objects.filter(annotation_count=2).count()

    # Count reviews with annotation count 1
    count_annotation_1 = UnannotatedReview.objects.filter(annotation_count=1).count()

    return count_annotation_3, count_annotation_2, count_annotation_1

# Example usage:
count_annotation_3, count_annotation_2, count_annotation_1 = count_reviews_by_annotation_count()
print("Number of reviews with annotation count 3:", count_annotation_3)
print("Number of reviews with annotation count 2:", count_annotation_2)
print("Number of reviews with annotation count 1:", count_annotation_1)
