from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard')),  # Redirigir a la vista del dashboard
    path('dashboard/', include('dashboard.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('landing-pages/', include('landing_pages.urls')),
    path('email-templates/', include('email_templates.urls')),
    path('groups/', include('groups.urls')),
    path('smtp/', include('smtp.urls')),
]
