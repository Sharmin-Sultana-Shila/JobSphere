from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    """
    This tells Django HOW to create users.
    We need this because we're using email instead of username.
    """

    def create_user(self, email, name, user_type, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, user_type=user_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, user_type='admin', password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom User model.
    Uses EMAIL to login instead of username.
    user_type tells us if this person is a seeker, recruiter, or admin.
    """

    USER_TYPE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_num = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # These fields are required for Django admin to work
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Tell Django to use our custom manager
    objects = UserManager()

    # Tell Django to use email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Company(models.Model):
    """
    Company that a recruiter belongs to.
    Created during recruiter onboarding.
    """
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Companies'


class JobSeeker(models.Model):
    """
    Extra profile info for job seekers.
    Connected to User with a OneToOneField.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    bio = models.TextField(blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True, null=True)
    career_goals = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    skills_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.name


class Recruiter(models.Model):
    """
    Extra profile info for recruiters.
    Connected to User AND Company.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    dept = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.name
