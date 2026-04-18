from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import (RegisterForm, LoginForm, SeekerOnboardingForm, RecruiterOnboardingForm,  UserProfilePicForm, SeekerProfileEditForm, RecruiterProfileEditForm, CompanyEditForm)
from .models import User, JobSeeker, Recruiter, Company


def register_view(request):
    # this is new comment
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
    Seeker dashboard showing:
    - Welcome message
    - Recent job posts
    - Quick links
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from recruitments.models import JobPost, Application

    # Get recent active job posts (latest 5)
    recent_jobs = JobPost.objects.filter(status='active', poster_type='recruiter')[:5]

    # Get seeker's applications count
    application_count = 0
    try:
        seeker = JobSeeker.objects.get(user=request.user)
        application_count = Application.objects.filter(seeker=seeker).count()
    except JobSeeker.DoesNotExist:
        pass

    return render(request, 'users/seeker_dashboard.html', {
        'recent_jobs': recent_jobs,
        'application_count': application_count
    })

def recruiter_dashboard_view(request):
    """
    Placeholder recruiter dashboard. We'll build this fully in EPIC-02.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/recruiter_dashboard.html')


def seeker_profile_view(request):
    """
    Shows the seeker's profile page.
    Displays all their info — bio, skills, CGPA, resume, etc.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_onboarding')

    return render(request, 'users/seeker_profile.html', {'seeker': seeker})


def seeker_profile_edit_view(request):
    """
    Lets seeker edit their profile info and profile picture.
    Two forms on one page — user info + seeker info.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_onboarding')

    if request.method == 'POST':
        user_form = UserProfilePicForm(request.POST, request.FILES, instance=request.user)
        seeker_form = SeekerProfileEditForm(request.POST, request.FILES, instance=seeker)

        if user_form.is_valid() and seeker_form.is_valid():
            user_form.save()
            seeker_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('seeker_profile')
    else:
        user_form = UserProfilePicForm(instance=request.user)
        seeker_form = SeekerProfileEditForm(instance=seeker)

    return render(request, 'users/seeker_profile_edit.html', {
        'user_form': user_form,
        'seeker_form': seeker_form,
        'seeker': seeker
    })


def recruiter_profile_view(request):
    """
    Shows the recruiter's profile page.
    Displays their company, designation, department.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('recruiter_onboarding')

    return render(request, 'users/recruiter_profile.html', {'recruiter': recruiter})


def recruiter_profile_edit_view(request):
    """
    Lets recruiter edit their profile, designation, dept, and company info.
    Three forms on one page — user info + recruiter info + company info.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('recruiter_onboarding')

    company = recruiter.company

    if request.method == 'POST':
        user_form = UserProfilePicForm(request.POST, request.FILES, instance=request.user)
        recruiter_form = RecruiterProfileEditForm(request.POST, instance=recruiter)
        company_form = CompanyEditForm(request.POST, request.FILES, instance=company)

        if user_form.is_valid() and recruiter_form.is_valid() and company_form.is_valid():
            user_form.save()
            recruiter_form.save()
            company_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('recruiter_profile')
    else:
        user_form = UserProfilePicForm(instance=request.user)
        recruiter_form = RecruiterProfileEditForm(instance=recruiter)
        company_form = CompanyEditForm(instance=company)

    return render(request, 'users/recruiter_profile_edit.html', {
        'user_form': user_form,
        'recruiter_form': recruiter_form,
        'company_form': company_form,
        'recruiter': recruiter
    })

