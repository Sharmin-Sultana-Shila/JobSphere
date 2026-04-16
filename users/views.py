from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm, SeekerOnboardingForm, RecruiterOnboardingForm
from .models import User, JobSeeker, Recruiter, Company


def register_view(request):
    """
    Handles user registration.
    1. Shows the register form
    2. When submitted, creates the User
    3. Redirects to the correct onboarding page based on role
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            user_type = form.cleaned_data['user_type']

            # Check if passwords match
            if password != confirm_password:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'users/register.html', {'form': form})

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return render(request, 'users/register.html', {'form': form})

            # Create the user
            user = User.objects.create_user(email=email, name=name, user_type=user_type, password=password)

            # Log them in immediately
            login(request, user)

            # Redirect to correct onboarding page
            if user_type == 'seeker':
                return redirect('seeker_onboarding')
            else:
                return redirect('recruiter_onboarding')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Handles user login.
    1. Shows the login form
    2. Checks email + password
    3. Redirects to correct dashboard based on role
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Try to authenticate
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # Redirect based on role
                if user.user_type == 'seeker':
                    return redirect('seeker_dashboard')
                elif user.user_type == 'recruiter':
                    return redirect('recruiter_dashboard')
                else:
                    return redirect('login')
            else:
                messages.error(request, 'Invalid email or password!')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """
    Logs out the user and redirects to login page.
    """
    logout(request)
    return redirect('login')


def seeker_onboarding_view(request):
    """
    After seeker registers, they fill out their profile.
    Creates a JobSeeker record linked to the logged-in user.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = SeekerOnboardingForm(request.POST, request.FILES)
        if form.is_valid():
            seeker = form.save(commit=False)
            seeker.user = request.user
            seeker.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('seeker_dashboard')
    else:
        form = SeekerOnboardingForm()

    return render(request, 'users/seeker_onboarding.html', {'form': form})


def recruiter_onboarding_view(request):
    """
    After recruiter registers, they fill out company info + their role.
    Creates a Company and Recruiter record.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = RecruiterOnboardingForm(request.POST, request.FILES)
        if form.is_valid():
            # Create or find the company
            company_name = form.cleaned_data['company_name']
            company_logo = form.cleaned_data.get('company_logo')
            company_location = form.cleaned_data.get('company_location')

            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'logo': company_logo,
                    'location': company_location
                }
            )

            # Create recruiter profile
            Recruiter.objects.create(
                user=request.user,
                company=company,
                designation=form.cleaned_data['designation'],
                dept=form.cleaned_data.get('dept', '')
            )

            messages.success(request, 'Profile created successfully!')
            return redirect('recruiter_dashboard')
    else:
        form = RecruiterOnboardingForm()

    return render(request, 'users/recruiter_onboarding.html', {'form': form})


def seeker_dashboard_view(request):
    """
    Placeholder seeker dashboard. We'll build this fully in EPIC-02.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/seeker_dashboard.html')


def recruiter_dashboard_view(request):
    """
    Placeholder recruiter dashboard. We'll build this fully in EPIC-02.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/recruiter_dashboard.html')
