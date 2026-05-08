from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import JobPost, Application
from .forms import JobPostForm, SeekerPostForm
from users.models import Recruiter, JobSeeker


def create_job_post_view(request):
    """
    Recruiter creates a new job post.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.poster = request.user
            job_post.poster_type = 'recruiter'
            job_post.save()
            messages.success(request, 'Job post created successfully!')
            return redirect('my_job_posts')
    else:
        form = JobPostForm()

    return render(request, 'recruitments/create_job_post.html', {'form': form})


def edit_job_post_view(request, post_id):
    """
    Recruiter edits an existing job post.
    Only the poster can edit their own post.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    job_post = get_object_or_404(JobPost, id=post_id, poster=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES, instance=job_post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job post updated successfully!')
            return redirect('my_job_posts')
    else:
        form = JobPostForm(instance=job_post)

    return render(request, 'recruitments/edit_job_post.html', {'form': form, 'job_post': job_post})


def toggle_job_post_status_view(request, post_id):
    """
    Recruiter closes or reopens a job post.
    If active → close it. If closed → reopen it.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    job_post = get_object_or_404(JobPost, id=post_id, poster=request.user)

    if job_post.status == 'active':
        job_post.status = 'closed'
        messages.success(request, f'"{job_post.title}" has been closed.')
    else:
        job_post.status = 'active'
        messages.success(request, f'"{job_post.title}" has been reopened.')

    job_post.save()
    return redirect('my_job_posts')


def my_job_posts_view(request):
    """
    Recruiter sees all their own job posts.
    Shows status (active/closed), application count, edit/close actions.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    job_posts = JobPost.objects.filter(poster=request.user, poster_type='recruiter')
    return render(request, 'recruitments/my_job_posts.html', {'job_posts': job_posts})


def job_list_view(request):
    """
    Seeker sees all active job posts.
    Supports search by keyword and filters by location, company, jobType.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from django.db.models import Q
    from users.models import Company

    # Start with all active recruiter posts
    job_posts = JobPost.objects.filter(status='active', poster_type='recruiter')

    # Get search and filter values from URL parameters
    search_query = request.GET.get('q', '').strip()
    location_filter = request.GET.get('location', '').strip()
    company_filter = request.GET.get('company', '').strip()
    job_type_filter = request.GET.get('job_type', '').strip()

    # Apply search — searches in title and description
    if search_query:
        job_posts = job_posts.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply location filter (case-insensitive partial match)
    if location_filter:
        job_posts = job_posts.filter(location__icontains=location_filter)

    # Apply job type filter (exact match)
    if job_type_filter:
        job_posts = job_posts.filter(job_type=job_type_filter)

    # Apply company filter — filter by recruiter's company name
    if company_filter:
        # Get all users (recruiters) whose company name matches
        matching_recruiters = Recruiter.objects.filter(
            company__name__icontains=company_filter
        ).values_list('user_id', flat=True)
        job_posts = job_posts.filter(poster_id__in=matching_recruiters)

    # Get list of all companies for the filter dropdown
    all_companies = Company.objects.all()

    # Job type choices for the dropdown
    job_type_choices = JobPost.JOB_TYPE_CHOICES

    return render(request, 'recruitments/job_list.html', {
        'job_posts': job_posts,
        'search_query': search_query,
        'location_filter': location_filter,
        'company_filter': company_filter,
        'job_type_filter': job_type_filter,
        'all_companies': all_companies,
        'job_type_choices': job_type_choices,
    })


def job_detail_view(request, post_id):
    """
    Shows full details of a single job post.
    Seekers see an Apply button and their preview ATS score.
    Recruiters see edit options.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    job_post = get_object_or_404(JobPost, id=post_id)

    # Check if seeker has already applied
    already_applied = False
    ats_preview = None

    if request.user.user_type == 'seeker':
        try:
            seeker = JobSeeker.objects.get(user=request.user)
            already_applied = Application.objects.filter(job_post=job_post, seeker=seeker).exists()

            # Calculate preview ATS score so seeker can see their match
            from .utils import calculate_ats_score
            ats_preview = calculate_ats_score(seeker, job_post)
        except JobSeeker.DoesNotExist:
            pass

    # Get the recruiter's company name
    # Get the recruiter's company info
    company_name = ''
    company_logo = None
    try:
        recruiter = Recruiter.objects.get(user=job_post.poster)
        if recruiter.company:
            company_name = recruiter.company.name
            if recruiter.company.logo:
                company_logo = recruiter.company.logo.url
    except Recruiter.DoesNotExist:
        pass

    return render(request, 'recruitments/job_detail.html', {
        'job_post': job_post,
        'already_applied': already_applied,
        'company_name': company_name,
        'company_logo': company_logo,
        'ats_preview': ats_preview,
    })

def create_seeker_post_view(request):
    """
    Seeker creates a reverse job post — showcasing their profile for recruiters.
    Uses SeekerPostForm which has fewer fields than recruiter's form.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    if request.method == 'POST':
        form = SeekerPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            post.poster_type = 'seeker'
            post.number_of_available_seats = 1
            post.save()
            messages.success(request, 'Your post has been published! Recruiters can now find you.')
            return redirect('my_seeker_posts')
    else:
        try:
            seeker = JobSeeker.objects.get(user=request.user)
            form = SeekerPostForm(initial={
                'skills_text': seeker.skills_text,
                'location': seeker.location,
            })
        except JobSeeker.DoesNotExist:
            form = SeekerPostForm()

    return render(request, 'recruitments/create_seeker_post.html', {'form': form})



def my_seeker_posts_view(request):
    """
    Seeker sees their own reverse posts.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    posts = JobPost.objects.filter(poster=request.user, poster_type='seeker')
    return render(request, 'recruitments/my_seeker_posts.html', {'posts': posts})


def seeker_posts_browser_view(request):
    """
    Recruiter browses all active seeker posts.
    Supports search and filters like the job listing page.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    from django.db.models import Q

    seeker_posts = JobPost.objects.filter(status='active', poster_type='seeker')

    # Get search and filter values
    search_query = request.GET.get('q', '').strip()
    location_filter = request.GET.get('location', '').strip()
    job_type_filter = request.GET.get('job_type', '').strip()
    skills_filter = request.GET.get('skills', '').strip()

    # Apply search
    if search_query:
        seeker_posts = seeker_posts.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply location filter
    if location_filter:
        seeker_posts = seeker_posts.filter(location__icontains=location_filter)

    # Apply job type filter
    if job_type_filter:
        seeker_posts = seeker_posts.filter(job_type=job_type_filter)

    # Apply skills filter
    if skills_filter:
        seeker_posts = seeker_posts.filter(skills_text__icontains=skills_filter)

    job_type_choices = JobPost.JOB_TYPE_CHOICES

    return render(request, 'recruitments/seeker_posts_browser.html', {
        'seeker_posts': seeker_posts,
        'search_query': search_query,
        'location_filter': location_filter,
        'job_type_filter': job_type_filter,
        'skills_filter': skills_filter,
        'job_type_choices': job_type_choices,
    })


def seeker_post_detail_view(request, post_id):
    """
    Recruiter views a single seeker's reverse post with their full profile.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    post = get_object_or_404(JobPost, id=post_id, poster_type='seeker')

    # Get the seeker's full profile
    seeker_profile = None
    try:
        seeker_profile = JobSeeker.objects.get(user=post.poster)
    except JobSeeker.DoesNotExist:
        pass

    return render(request, 'recruitments/seeker_post_detail.html', {
        'post': post,
        'seeker_profile': seeker_profile
    })


# Saifa's Work:
def apply_for_job_view(request, post_id):
    """
    Seeker applies for a job post.
    Calculates ATS score, creates Application, increments application_count.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    job_post = get_object_or_404(JobPost, id=post_id, status='active', poster_type='recruiter')

    # Get the seeker profile
    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        messages.error(request, 'Please complete your profile before applying.')
        return redirect('seeker_onboarding')

    # Check if already applied
    if Application.objects.filter(job_post=job_post, seeker=seeker).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('job_detail', post_id=post_id)

    # Calculate ATS score
    from .utils import calculate_ats_score
    ats_score = calculate_ats_score(seeker, job_post)

    # Create the application
    Application.objects.create(
        job_post=job_post,
        seeker=seeker,
        status='applied',
        ats_score=ats_score
    )

    # Increment application count on the job post
    job_post.application_count = job_post.application_count + 1
    job_post.save()

    messages.success(request, f'Application submitted! Your ATS score: {ats_score}/100')
    return redirect('my_applications')


def withdraw_application_view(request, application_id):
    """
    Seeker withdraws their application.
    Only applications in 'applied' status can be withdrawn.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_dashboard')

    application = get_object_or_404(Application, id=application_id, seeker=seeker)

    # Only allow withdrawal if status is 'applied'
    if application.status != 'applied':
        messages.error(request, 'You can only withdraw applications that are still pending review.')
        return redirect('my_applications')

    # Decrement application count
    job_post = application.job_post
    if job_post.application_count > 0:
        job_post.application_count = job_post.application_count - 1
        job_post.save()

    # Delete the application
    application.delete()

    messages.success(request, 'Application withdrawn successfully.')
    return redirect('my_applications')


def my_applications_view(request):
    """
    Seeker sees all their applications with status chips.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_onboarding')

    applications = Application.objects.filter(seeker=seeker).select_related('job_post')

    return render(request, 'recruitments/my_applications.html', {
        'applications': applications
    })

def applicants_list_view(request, post_id):
    """
    Recruiter views all applicants for a specific job post.
    Applicants are ranked by ATS score (highest first).
    Supports filtering by status.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    # Ensure the recruiter owns this job post
    job_post = get_object_or_404(JobPost, id=post_id, poster=request.user)

    # Get applications ranked by ATS score
    applications = Application.objects.filter(job_post=job_post).order_by('-ats_score')

    # Apply status filter if provided
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Count for each status to show in chips
    all_apps = Application.objects.filter(job_post=job_post)
    status_counts = {
        'all': all_apps.count(),
        'applied': all_apps.filter(status='applied').count(),
        'review': all_apps.filter(status='review').count(),
        'shortlisted': all_apps.filter(status='shortlisted').count(),
        'selected': all_apps.filter(status='selected').count(),
        'rejected': all_apps.filter(status='rejected').count(),
    }

    return render(request, 'recruitments/applicants_list.html', {
        'job_post': job_post,
        'applications': applications,
        'status_filter': status_filter,
        'status_counts': status_counts,
    })


def applicant_detail_view(request, application_id):
    """
    Recruiter views the full detail of one applicant.
    Shows seeker profile, resume, skills match, and status update dropdown.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    application = get_object_or_404(Application, id=application_id)

    # Ensure recruiter owns the related job post
    if application.job_post.poster != request.user:
        messages.error(request, 'You do not have permission to view this applicant.')
        return redirect('my_job_posts')

    seeker = application.seeker
    job_post = application.job_post

    # Calculate which job skills the seeker has (for skills match display)
    seeker_skills = [s.strip().lower() for s in (seeker.skills_text or '').split(',') if s.strip()]
    job_skills_raw = [s.strip() for s in (job_post.skills_text or '').split(',') if s.strip()]

    skills_match = []
    for skill in job_skills_raw:
        skills_match.append({
            'name': skill,
            'matched': skill.lower() in seeker_skills
        })

    # Status choices for dropdown
    status_choices = Application.STATUS_CHOICES

    return render(request, 'recruitments/applicant_detail.html', {
        'application': application,
        'seeker': seeker,
        'job_post': job_post,
        'skills_match': skills_match,
        'status_choices': status_choices,
    })


def update_application_status_view(request, application_id):
    """
    Recruiter updates the status of an application.
    Triggers a notification to the seeker.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    application = get_object_or_404(Application, id=application_id)

    # Ensure recruiter owns the related job post
    if application.job_post.poster != request.user:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('my_job_posts')

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]

        if new_status in valid_statuses:
            old_status = application.status
            application.status = new_status
            application.save()

            # Trigger notification if status actually changed
            if old_status != new_status:
                from updates.utils import create_notification
                seeker_user = application.seeker.user
                job_title = application.job_post.title

                create_notification(
                    user=seeker_user,
                    notif_type='status',
                    title=f'Application status updated: {application.get_status_display()}',
                    content=f'Your application for "{job_title}" is now {application.get_status_display()}.'
                )

            messages.success(request, f'Status updated to {application.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status value.')

    return redirect('applicant_detail', application_id=application_id)
def schedule_interview_view(request, application_id):
    """
    Recruiter schedules an interview for an applicant.
    Only shortlisted applicants can be scheduled for interviews.
    Triggers a notification to the seeker.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    application = get_object_or_404(Application, id=application_id)

    # Ensure recruiter owns the related job post
    if application.job_post.poster != request.user:
        messages.error(request, 'You do not have permission.')
        return redirect('my_job_posts')

    # Must be shortlisted first
    if application.status != 'shortlisted':
        messages.error(request, 'You can only schedule interviews for shortlisted applicants.')
        return redirect('applicant_detail', application_id=application_id)

    from .forms import InterviewScheduleForm
    from .models import Interview

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.status = 'scheduled'
            interview.save()

            # Trigger notification to seeker
            from updates.utils import create_notification
            create_notification(
                user=application.seeker.user,
                notif_type='interview',
                title=f'Interview scheduled for {application.job_post.title}',
                content=f'Your interview is scheduled on {interview.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}. Check your interviews page for details.'
            )

            messages.success(request, f'Interview scheduled with {application.seeker.user.name}.')
            return redirect('interview_list')
    else:
        form = InterviewScheduleForm()

    return render(request, 'recruitments/schedule_interview.html', {
        'form': form,
        'application': application
    })

def cancel_interview_view(request, interview_id):
    """
    Recruiter cancels a scheduled interview.
    Triggers a notification to the seeker.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    from .models import Interview
    interview = get_object_or_404(Interview, id=interview_id)

    # Ensure recruiter owns the related job post
    if interview.application.job_post.poster != request.user:
        messages.error(request, 'You do not have permission.')
        return redirect('my_job_posts')

    if interview.status == 'scheduled':
        interview.status = 'cancelled'
        interview.save()

        # Trigger notification to seeker
        from updates.utils import create_notification
        create_notification(
            user=interview.application.seeker.user,
            notif_type='interview',
            title=f'Interview cancelled for {interview.application.job_post.title}',
            content=f'Your interview scheduled for {interview.scheduled_at.strftime("%B %d, %Y at %I:%M %p")} has been cancelled.'
        )

        messages.success(request, 'Interview cancelled.')
    else:
        messages.error(request, 'Only scheduled interviews can be cancelled.')

    return redirect('interview_list')
def interview_list_view(request):
    """
    Recruiter sees all their interviews.
    Scheduled interviews first (newest first), then completed, then cancelled.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    from .models import Interview
    from django.db.models import Case, When, IntegerField

    # Custom ordering: scheduled first, then completed, then cancelled
    interviews = Interview.objects.filter(
        application__job_post__poster=request.user
    ).select_related(
        'application', 'application__seeker', 'application__job_post'
    ).annotate(
        status_order=Case(
            When(status='scheduled', then=0),
            When(status='completed', then=1),
            When(status='cancelled', then=2),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-scheduled_at')

    return render(request, 'recruitments/interview_list.html', {
        'interviews': interviews
    })

def interview_detail_seeker_view(request, interview_id):
    """
    Seeker views the details of their interview.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    from .models import Interview

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_dashboard')

    interview = get_object_or_404(Interview, id=interview_id, application__seeker=seeker)

    return render(request, 'recruitments/interview_detail_seeker.html', {
        'interview': interview
    })


def my_interviews_seeker_view(request):
    """
    Seeker sees all their interviews.
    """
    if not request.user.is_authenticated or request.user.user_type != 'seeker':
        return redirect('login')

    from .models import Interview

    try:
        seeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        return redirect('seeker_dashboard')

    interviews = Interview.objects.filter(
        application__seeker=seeker
    ).select_related('application', 'application__job_post').order_by('-scheduled_at')

    return render(request, 'recruitments/my_interviews.html', {
        'interviews': interviews
    })
def submit_interview_feedback_view(request, interview_id):
    """
    Recruiter submits interview outcome and feedback.
    Updates the related Application status.
    Creates a notification for the seeker.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    from .models import Interview
    from .forms import InterviewFeedbackForm

    interview = get_object_or_404(Interview, id=interview_id)

    # Ensure recruiter owns the related job post
    if interview.application.job_post.poster != request.user:
        messages.error(request, 'You do not have permission.')
        return redirect('my_job_posts')

    if interview.status == 'cancelled':
        messages.error(request, 'Cannot submit feedback for a cancelled interview.')
        return redirect('interview_list')

    if request.method == 'POST':
        form = InterviewFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.status = 'completed'
            feedback.save()

            # Update application status based on outcome
            application = interview.application
            if feedback.selection_status == 'selected':
                application.status = 'selected'
            elif feedback.selection_status == 'rejected':
                application.status = 'rejected'
            application.save()

            # Trigger notification to seeker
            from updates.utils import create_notification
            seeker_user = application.seeker.user
            job_title = application.job_post.title

            if feedback.selection_status == 'selected':
                notif_title = f'Interview result: Selected for {job_title}!'
                notif_content = f'Congratulations! You have been selected for the {job_title} position.'
            else:
                notif_title = f'Interview result: Not selected for {job_title}'
                notif_content = 'Thank you for interviewing. Unfortunately you were not selected. Check feedback for improvement areas.'

            create_notification(
                user=seeker_user,
                notif_type='interview',
                title=notif_title,
                content=notif_content
            )

            messages.success(request, 'Feedback submitted successfully.')
            return redirect('interview_list')
    else:
        form = InterviewFeedbackForm(instance=interview)

    return render(request, 'recruitments/submit_feedback.html', {
        'form': form,
        'interview': interview
    })

# reviewed


def like_post_view(request, post_id):
    """
    Toggle like on a job post.
    If already liked, unlike it. If not liked, like it.
    Sends notification to the post owner when liked.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from .models import PostLike
    from updates.utils import create_notification
    job_post = get_object_or_404(JobPost, id=post_id)

    existing_like = PostLike.objects.filter(job_post=job_post, user=request.user)
    if existing_like.exists():
        existing_like.delete()
    else:
        PostLike.objects.create(job_post=job_post, user=request.user)

        # Send notification to post owner (don't notify yourself)
        if job_post.poster != request.user:
            create_notification(
                user=job_post.poster,
                notif_type='status',
                title=f'{request.user.name} liked your post',
                content=f'{request.user.name} liked your post "{job_post.title}".'
            )

    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('feed')


def comment_post_view(request, post_id):
    """
    Add a comment to a job post.
    Sends notification to the post owner when commented.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from .models import PostComment
    from updates.utils import create_notification
    job_post = get_object_or_404(JobPost, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('comment_content', '').strip()
        if content:
            PostComment.objects.create(
                job_post=job_post,
                user=request.user,
                content=content
            )

            # Send notification to post owner (don't notify yourself)
            if job_post.poster != request.user:
                create_notification(
                    user=job_post.poster,
                    notif_type='status',
                    title=f'{request.user.name} commented on your post',
                    content=f'{request.user.name} commented on "{job_post.title}": {content[:80]}'
                )

    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('feed')


def feed_view(request):
    """
    LinkedIn-style feed page.
    Seekers see recruiter job posts.
    Recruiters see seeker reverse posts.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from .models import PostLike, PostComment

    if request.user.user_type == 'seeker':
        posts = JobPost.objects.filter(status='active', poster_type='recruiter')
    elif request.user.user_type == 'recruiter':
        posts = JobPost.objects.filter(status='active', poster_type='seeker')
    else:
        posts = JobPost.objects.none()

    # Build feed data with like/comment info
    feed_data = []
    for post in posts:
        like_count = PostLike.objects.filter(job_post=post).count()
        user_liked = PostLike.objects.filter(job_post=post, user=request.user).exists()
        comments = PostComment.objects.filter(job_post=post).select_related('user')[:5]
        comment_count = PostComment.objects.filter(job_post=post).count()

        # Get poster profile info
        poster_pic = None
        poster_company = ''
        poster_designation = ''
        if post.poster.profile_pic:
            poster_pic = post.poster.profile_pic.url

        if post.poster_type == 'recruiter':
            try:
                rec = Recruiter.objects.get(user=post.poster)
                if rec.company:
                    poster_company = rec.company.name
                poster_designation = rec.designation or ''
            except Recruiter.DoesNotExist:
                pass
        else:
            try:
                seeker_profile = JobSeeker.objects.get(user=post.poster)
                poster_designation = seeker_profile.education or ''
            except JobSeeker.DoesNotExist:
                pass

        feed_data.append({
            'post': post,
            'like_count': like_count,
            'user_liked': user_liked,
            'comments': comments,
            'comment_count': comment_count,
            'poster_pic': poster_pic,
            'poster_company': poster_company,
            'poster_designation': poster_designation,
        })

    return render(request, 'recruitments/feed.html', {
        'feed_data': feed_data,
    })
