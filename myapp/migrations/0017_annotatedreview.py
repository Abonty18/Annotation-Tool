# Generated by Django 4.2.7 on 2024-02-14 19:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0016_reviewlock"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnnotatedReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("student1_annotation", models.IntegerField(blank=True, null=True)),
                ("student2_annotation", models.IntegerField(blank=True, null=True)),
                ("student3_annotation", models.IntegerField(blank=True, null=True)),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="myapp.unannotatedreview",
                    ),
                ),
                (
                    "student1",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student1_annotated_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student2_annotated_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student3",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student3_annotated_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
