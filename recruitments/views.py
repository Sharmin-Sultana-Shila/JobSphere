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
        form = JobPostForm(request.POST)
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
        form = JobPostForm(request.POST, instance=job_post)
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
    Shows search bar and filter options (built fully in EPIC-03).
    """
    if not request.user.is_authenticated:
        return redirect('login')

    job_posts = JobPost.objects.filter(status='active', poster_type='recruiter')
    return render(request, 'recruitments/job_list.html', {'job_posts': job_posts})


def job_detail_view(request, post_id):
    """
    Shows full details of a single job post.
    Seekers see an Apply button. Recruiters see edit options.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    job_post = get_object_or_404(JobPost, id=post_id)

    # Check if seeker has already applied
    already_applied = False
    if request.user.user_type == 'seeker':
        try:
            seeker = JobSeeker.objects.get(user=request.user)
            already_applied = Application.objects.filter(job_post=job_post, seeker=seeker).exists()
        except JobSeeker.DoesNotExist:
            pass

    # Get the recruiter's company name
    company_name = ''
    try:
        recruiter = Recruiter.objects.get(user=job_post.poster)
        if recruiter.company:
            company_name = recruiter.company.name
    except Recruiter.DoesNotExist:
        pass

    return render(request, 'recruitments/job_detail.html', {
        'job_post': job_post,
        'already_applied': already_applied,
        'company_name': company_name
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



def seeker_posts_browser_view(request):
    """
    Recruiter browses all active seeker posts.
    These are reverse posts where seekers showcase themselves.
    """
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    seeker_posts = JobPost.objects.filter(status='active', poster_type='seeker')
    return render(request, 'recruitments/seeker_posts_browser.html', {'seeker_posts': seeker_posts})


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

