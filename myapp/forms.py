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

    SOFTWARE_COURSES_CHOICES = [
        ('Software Requirement and Specifications', 'Software Requirement and Specifications'),
        ('Software Security', 'Software Security'),
        ('Software Design and Architectures', 'Software Design and Architectures'),
        ('Software Testing and Quality Assurance', 'Software Testing and Quality Assurance'),
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

class InviteAnnotatorForm(forms.Form):
    email = forms.EmailField(label='Annotator Email', required=True)
    
class ProjectForm(forms.ModelForm):
    uploaded_file = forms.FileField(label="Upload File", required=True)
    review_column = forms.CharField(label="Review Column", required=True)
    annotators_count = forms.IntegerField(label="Number of Annotators", min_value=1, required=True)
    sections_count = forms.IntegerField(label="Number of Sections/Labels", min_value=1, required=True)
    labels = forms.CharField(label="Labels", help_text="Comma-separated list of labels", required=True)
    output_format = forms.ChoiceField(label="Output Format", choices=[('csv', 'CSV'), ('json', 'JSON')], required=True)

    class Meta:
        model = StudentProject
        fields = ['name', 'description', 'start_date', 'end_date', 'uploaded_file', 'review_column', 'annotators_count', 'sections_count', 'labels', 'output_format']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date should be after the start date.")
        return cleaned_data
