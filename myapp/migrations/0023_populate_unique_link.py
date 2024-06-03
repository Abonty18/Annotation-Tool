from django.db import migrations, models
import django.utils.crypto

def populate_unique_link(apps, schema_editor):
    StudentProject = apps.get_model('myapp', 'StudentProject')
    for project in StudentProject.objects.all():
        if not project.unique_link:
            project.unique_link = django.utils.crypto.get_random_string(length=32)
            project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_studentproject_annotators_count_and_more'),  # Use the actual name of the latest migration
    ]

    operations = [
        migrations.RunPython(populate_unique_link),
    ]
