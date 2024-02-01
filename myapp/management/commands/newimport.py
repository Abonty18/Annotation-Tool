from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview
import pandas as pd

class Command(BaseCommand):
    help = 'Import reviews from an Excel file into UnannotatedReview model'

    def handle(self, *args, **kwargs):
        excel_file_path = 'ff.xlsx'  # Ensure this path is correct
        imported_count = 0

        try:
            df = pd.read_excel(excel_file_path)
            for index, row in df.iterrows():
                # Assuming 'ReviewContent' is the column name. Adjust as necessary.
                review_content = row['Review']  # More explicit column reference
                obj, created = UnannotatedReview.objects.get_or_create(content=review_content)
                if created:
                    imported_count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported_count} reviews from Excel.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
