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
]
