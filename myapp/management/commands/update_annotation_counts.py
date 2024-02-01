# myapp/management/commands/update_annotation_counts.py

import json
from collections import defaultdict
from django.core.management.base import BaseCommand
from myapp.models import CustomUser, StudentAnnotation

class Command(BaseCommand):
    help = 'Update annotation counts from a JSON backup file'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the JSON backup file')

    def handle(self, *args, **kwargs):
        backup_file = kwargs['backup_file']

        try:
            # Reset all annotation counts to zero before updating
            CustomUser.objects.update(annotation_count=0)

            # Create a dictionary to accumulate annotation counts
            annotation_counts = defaultdict(int)

            with open(backup_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for item in data:
                if item['model'] == 'myapp.studentannotation':
                    fields = item['fields']
                    for student_key in ['student1', 'student2', 'student3']:
                        student_id = fields.get(student_key)
                        if student_id:
                            # Accumulate counts in the dictionary
                            annotation_counts[student_id] += 1

            # Update each user's annotation count based on accumulated counts
            for user_id, count in annotation_counts.items():
                user = CustomUser.objects.get(pk=user_id)
                user.annotation_count = count
                user.save()

            self.stdout.write(self.style.SUCCESS('Successfully updated annotation counts from backup'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
