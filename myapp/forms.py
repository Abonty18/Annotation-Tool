from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, StudentProject
class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    age = forms.IntegerField(required=False)

    WORKING_EXPERIENCE_CHOICES = [
        (0, '0-1 years'),
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
        ('Software Requirement and Specifications', 'Software Requirement and Specifications'),
        ('Software Security', 'Software Security'),
        ('Software Design and Architectures', 'Software Design and Architectures'),
        ('Software Testing and Quality Assurance', 'Software Testing and Quality Assurance'),
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
    def __init__(self, *args, **kwargs):
        show_email_field = kwargs.pop('show_email_field', True)
        super(StudentForm, self).__init__(*args, **kwargs)
        if not show_email_field:
            del self.fields['email']


class AppReviewForm(forms.Form):
    app_link = forms.URLField(label="App Link", required=True)
    start_date = forms.DateField(label="Start Date", widget=forms.SelectDateWidget)
    end_date = forms.DateField(label="End Date", widget=forms.SelectDateWidget)


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if end_date < start_date:
            raise forms.ValidationError("End date should be after the start date.")
        return cleaned_data
    
class ProjectForm(forms.ModelForm):
    # Add a file upload field to the form
    uploaded_file = forms.FileField(label="Upload File", required=True)

    class Meta:
        model = StudentProject
        fields = ['name', 'description', 'start_date', 'end_date', 'uploaded_file']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date should be after the start date.")
        return cleaned_data