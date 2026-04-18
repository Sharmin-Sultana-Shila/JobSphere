from django import forms
from .models import User, JobSeeker, Recruiter, Company


class RegisterForm(forms.Form):
    # tetsing the project
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Confirm Password'
    }))
    user_type = forms.ChoiceField(choices=[
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ], widget=forms.RadioSelect(attrs={
        'class': 'form-radio'
    }))


class LoginForm(forms.Form):
    """
    Simple login form. Email + password.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))


class SeekerOnboardingForm(forms.ModelForm):
    """
    After a seeker registers, they fill this out.
    Bio, CGPA, skills, experience, resume, career goals.
    """
    class Meta:
        model = JobSeeker
        fields = ['bio', 'cgpa', 'experience_years', 'education', 'career_goals',
                  'resume', 'location', 'skills_text']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Tell us about yourself...',
                'rows': 3
            }),
            'cgpa': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 3.50',
                'step': '0.01',
                'min': '0',
                'max': '4'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0'
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. BSc in Computer Science'
            }),
            'career_goals': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'What are your career goals?',
                'rows': 3
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Dhaka, Bangladesh'
            }),
            'skills_text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Python, Django, JavaScript, SQL',
                'rows': 2
            }),
        }
class RecruiterOnboardingForm(forms.Form):
    """
    After a recruiter registers, they fill this out.
    Company name, logo, designation, department.
    """
    company_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Company Name'
    }))
    company_logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-input'
    }))
    company_location = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Company Location'
    }))
    designation = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your Designation (e.g. HR Manager)'
    }))
    dept = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Department (e.g. Human Resources)'
    }))

class UserProfilePicForm(forms.ModelForm):
    """
    Lets any user update their profile picture and phone number.
    """
    class Meta:
        model = User
        fields = ['profile_pic', 'phone_num']
        widgets = {
            'profile_pic': forms.FileInput(attrs={
                'class': 'form-input'
            }),
            'phone_num': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. +880 1712 345678'
            }),
        }


class SeekerProfileEditForm(forms.ModelForm):
    """
    Lets seeker edit their profile info after onboarding.
    Same fields as onboarding but used for editing.
    """
    class Meta:
        model = JobSeeker
        fields = ['bio', 'cgpa', 'experience_years', 'education', 'career_goals',
                  'resume', 'location', 'skills_text']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3
            }),
            'cgpa': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'max': '4'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0'
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'career_goals': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'skills_text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2
            }),
        }


class RecruiterProfileEditForm(forms.ModelForm):
    """
    Lets recruiter edit their designation and department.
    """
    class Meta:
        model = Recruiter
        fields = ['designation', 'dept']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'dept': forms.TextInput(attrs={
                'class': 'form-input'
            }),
        }


class CompanyEditForm(forms.ModelForm):
    """
    Lets recruiter edit their company info.
    """
    class Meta:
        model = Company
        fields = ['name', 'logo', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input'
            }),
        }
