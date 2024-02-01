from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview
import pandas as pd

class Command(BaseCommand):
    help = 'Import reviews from an Excel file into UnannotatedReview model'

    def handle(self, *args, **kwargs):
        excel_file_path = 'student.xlsx'  # Update with the path to your Excel file
        imported_count = 0  # Counter for imported reviews

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file_path)

            # Iterate through the DataFrame and create UnannotatedReview objects
            for index, row in df.iterrows():
                review_content = row.iloc[0]  # Corrected to use .iloc[0]
                UnannotatedReview.objects.create(content=review_content)
                imported_count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully importeddd {imported_count} reviews from Excel'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
