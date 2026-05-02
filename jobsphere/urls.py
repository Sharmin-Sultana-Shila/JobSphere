from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('users/', include('users.urls')),
    path('recruitments/', include('recruitments.urls')),
    path('updates/', include('updates.urls')),
]

# This lets Django serve uploaded files (profile pics, resumes) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
