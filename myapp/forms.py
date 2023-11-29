from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    has_taken_software_engineering_course = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'department', 'has_taken_software_engineering_course', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
