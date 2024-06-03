from django.db import migrations, models
import django.utils.crypto

def populate_unique_links(apps, schema_editor):
    StudentProject = apps.get_model('myapp', 'StudentProject')
    for project in StudentProject.objects.all():
        if not project.unique_link or project.unique_link == "":
            project.unique_link = django.utils.crypto.get_random_string(length=32)
            project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_merge_20240602_0033'),  # The last applied migration
    ]

    operations = [
        migrations.RunPython(populate_unique_links),
    ]
