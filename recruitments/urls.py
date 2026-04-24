from django.urls import path
from . import views

urlpatterns = [
    # Recruiter: manage job posts
    path('create/', views.create_job_post_view, name='create_job_post'),
    path('edit/<int:post_id>/', views.edit_job_post_view, name='edit_job_post'),
    path('toggle/<int:post_id>/', views.toggle_job_post_status_view, name='toggle_job_post_status'),
    path('my-posts/', views.my_job_posts_view, name='my_job_posts'),

    # Seeker: browse jobs
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/<int:post_id>/', views.job_detail_view, name='job_detail'),

    # STORY-11: Reverse job posting
    path('seeker-post/create/', views.create_seeker_post_view, name='create_seeker_post'),
    path('seeker-post/my-posts/', views.my_seeker_posts_view, name='my_seeker_posts'),
    path('seeker-posts/', views.seeker_posts_browser_view, name='seeker_posts_browser'),
    path('seeker-posts/<int:post_id>/', views.seeker_post_detail_view, name='seeker_post_detail'),

    # STORY-14: Application (apply, withdraw, my applications)
    path('apply/<int:post_id>/', views.apply_for_job_view, name='apply_for_job'),
    path('withdraw/<int:application_id>/', views.withdraw_application_view, name='withdraw_application'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
]
