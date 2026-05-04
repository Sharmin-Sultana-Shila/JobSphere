from django.db import models
from users.models import User, JobSeeker, Recruiter
from django.utils import timezone

class Skill(models.Model):
    """
    A skill like 'Python', 'Django', 'SQL', etc.
    Has a category like 'programming', 'database', 'design'.
    """
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class SeekerSkill(models.Model):
    """
    Links a JobSeeker to a Skill with a proficiency level.
    Example: Seeker "Sharmin" has skill "Python" at level "advanced".
    """
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='seeker_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='beginner')

    class Meta:
        unique_together = ('seeker', 'skill')

    def __str__(self):
        return f"{self.seeker.user.name} - {self.skill.name} ({self.proficiency_level})"


class JobPost(models.Model):
    """
    A job post created by a recruiter OR a reverse post by a seeker.
    Contains title, description, salary, location, skills, deadline, etc.
    """
    POSTER_TYPE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('seeker', 'Seeker'),
    ]

    JOB_TYPE_CHOICES = [
        ('fullTime', 'Full Time'),
        ('partTime', 'Part Time'),
        ('remote', 'Remote'),
        ('contract', 'Contract'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')
    poster_type = models.CharField(max_length=10, choices=POSTER_TYPE_CHOICES, default='recruiter')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES, default='fullTime')
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_available_seats = models.IntegerField(default=1)
    required_experience = models.FloatField(default=0)
    skills_text = models.TextField(blank=True, null=True)
    application_count = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='job_post_images/', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class JobPostSkill(models.Model):
    """
    Links a JobPost to a Skill with a weightage.
    Example: Job "Django Developer" needs skill "Python" with weightage 0.8 (very important).
    """
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='job_post_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weightage = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('job_post', 'skill')

    def __str__(self):
        return f"{self.job_post.title} - {self.skill.name}"


class Application(models.Model):
    """
    When a seeker applies for a job, this record is created.
    Tracks status from applied → review → shortlisted → selected/rejected.
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    ats_score = models.FloatField(default=0)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job_post', 'seeker')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.seeker.user.name} → {self.job_post.title}"


class Interview(models.Model):
    """
    When a recruiter schedules an interview for a shortlisted applicant.
    Stores date, location, meeting link, and outcome feedback.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    SELECTION_CHOICES = [
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    selection_status = models.CharField(max_length=10, choices=SELECTION_CHOICES, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    improvement_areas = models.TextField(blank=True, null=True)
    tech_skill_to_develop = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interview: {self.application.seeker.user.name} for {self.application.job_post.title}"

class PostLike(models.Model):
    """
    Tracks likes on job posts.
    """
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_post', 'user')

    def __str__(self):
        return f"{self.user.name} liked {self.job_post.title}"


class PostComment(models.Model):
    """
    Comments on job posts.
    """
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.name}: {self.content[:30]}"
