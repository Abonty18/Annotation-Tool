# Generated by Django 4.2.7 on 2024-05-09 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0020_studentproject_description_studentproject_end_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentproject",
            name="uploaded_file",
            field=models.FileField(default=" ", upload_to="uploads/%Y/%m/%d/"),
            preserve_default=False,
        ),
    ]
