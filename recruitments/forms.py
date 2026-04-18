from django import forms
from .models import JobPost


class JobPostForm(forms.ModelForm):
    """
    Form for recruiter to create or edit a job post.
    """
    class Meta:
        model = JobPost
        fields = ['title', 'description', 'location', 'job_type', 'salary',
                  'number_of_available_seats', 'required_experience', 'skills_text',
                  'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Senior Django Developer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe the role, responsibilities, and requirements...',
                'rows': 5
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Dhaka, Bangladesh'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 50000',
                'step': '0.01'
            }),
            'number_of_available_seats': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '1',
                'min': '1'
            }),
            'required_experience': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'step': '0.5',
                'min': '0'
            }),
            'skills_text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Python, Django, PostgreSQL, REST API',
                'rows': 2
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
        }


class SeekerPostForm(forms.ModelForm):
    """
    Form for seeker to create a reverse job post.
    Fewer fields than the recruiter's JobPostForm.
    """
    class Meta:
        model = JobPost
        fields = ['title', 'description', 'location', 'job_type', 'salary',
                  'required_experience', 'skills_text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Experienced Django Developer Seeking Opportunities'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Tell recruiters about yourself, what you are looking for...',
                'rows': 5
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Dhaka, Bangladesh'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Expected salary e.g. 50000',
                'step': '0.01'
            }),
            'required_experience': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'step': '0.5',
                'min': '0'
            }),
            'skills_text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Python, Django, JavaScript, SQL',
                'rows': 2
            }),
        }
