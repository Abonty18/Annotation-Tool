# Generated by Django 4.2.7 on 2024-02-01 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0013_remove_customuser_has_taken_software_course"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="annotation_count",
            field=models.IntegerField(default=0),
        ),
    ]