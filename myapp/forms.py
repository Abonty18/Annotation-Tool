# myapp/forms.py

from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Student
        
        fields = ['name', 'email', 'department', 'program', 'graduation_year', 'password']
