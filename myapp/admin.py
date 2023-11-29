from django.contrib import admin
from .models import CustomUser, Review, UnannotatedReview, Annotation, StudentAnnotation, StudentProject

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Review)
admin.site.register(UnannotatedReview)
admin.site.register(Annotation)
admin.site.register(StudentAnnotation)
admin.site.register(StudentProject)
