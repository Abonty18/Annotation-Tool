# Generated by Django 4.2.7 on 2024-02-02 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0014_customuser_annotation_count"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="annotation",
            unique_together=set(),
        ),
    ]