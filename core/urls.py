from django.urls import path, include
from . import views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('campaigns/', include('campaigns.urls')),
    path('landing-pages/', include('landing_pages.urls')),
    path('email-templates/', include('email_templates.urls')),
    path('groups/', include('groups.urls')),
    path('smtp/', include('smtp.urls')),
    path('login/', views.login_view, name='login'),
    path('', redirect('dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
