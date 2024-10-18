from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from core.views import login_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard')),  # Redirigir a la vista del dashboard
    path('login/', login_view, name='login'),  # Redirigir a la vista de login
    path('dashboard/', include('dashboard.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('landing-pages/', include('landing_pages.urls')),
    path('email-templates/', include('email_templates.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('groups/', include('groups.urls')),
    path('smtp/', include('smtp.urls')),
    path('webhooks/', include('webhooks.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
