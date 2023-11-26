import os
import django
import pandas as pd

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

# Import the UnannotatedReview model
from myapp.models import UnannotatedReview

# Define the path to your Excel file
excel_file_path = '../../data/testing2'

def populate_unannotated_reviews():
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(excel_file_path)

        # Iterate through the DataFrame and create UnannotatedReview objects
        for index, row in df.iterrows():
            review_content = row[0]  # Assuming the review content is in the first column
            # Create a new UnannotatedReview object
            UnannotatedReview.objects.create(content=review_content)

        print("Unannotated reviews populated successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    populate_unannotated_reviews()
