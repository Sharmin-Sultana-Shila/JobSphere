from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('onboarding/seeker/', views.seeker_onboarding_view, name='seeker_onboarding'),
    path('onboarding/recruiter/', views.recruiter_onboarding_view, name='recruiter_onboarding'),
    path('dashboard/seeker/', views.seeker_dashboard_view, name='seeker_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard_view, name='recruiter_dashboard'),

    
    path('profile/seeker/', views.seeker_profile_view, name='seeker_profile'),
    path('profile/seeker/edit/', views.seeker_profile_edit_view, name='seeker_profile_edit'),
    path('profile/recruiter/', views.recruiter_profile_view, name='recruiter_profile'),
    path('profile/recruiter/edit/', views.recruiter_profile_edit_view, name='recruiter_profile_edit'),
]


