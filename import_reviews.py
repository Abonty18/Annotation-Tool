from django.core.management.base import BaseCommand
from myapp.models import UnannotatedReview
import pandas as pd

class Command(BaseCommand):
    help = 'Import reviews from an Excel file into UnannotatedReview model'

    def handle(self, *args, **kwargs):
        excel_file_path = 'testing2.xlsx'  # Update with the path to your Excel file

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file_path)

            # Iterate through the DataFrame and create UnannotatedReview objects
            for index, row in df.iterrows():
                review_content = row[0]  # Adjust if your Excel structure is different
                UnannotatedReview.objects.create(content=review_content)

            self.stdout.write(self.style.SUCCESS('Successfully imported reviews from Excel'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
