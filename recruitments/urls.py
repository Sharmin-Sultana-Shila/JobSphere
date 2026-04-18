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
]
