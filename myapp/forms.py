from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    age = forms.IntegerField(required=False)

    WORKING_EXPERIENCE_CHOICES = [
        (0, '0 years'),
        (1, '1-2 years'),
        (3, '3-5 years'),
        (5, '5 years+'),
    ]
    working_experience = forms.ChoiceField(
        choices=WORKING_EXPERIENCE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )

    # Software related courses (dynamic list can be defined elsewhere or fetched from a database)
    SOFTWARE_COURSES_CHOICES = [
        ('course1', 'Course 1'),
        ('course2', 'Course 2'),
        # ... more courses ...
    ]
    software_related_courses = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=SOFTWARE_COURSES_CHOICES,
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'department', 'age', 'working_experience', 'software_related_courses', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
