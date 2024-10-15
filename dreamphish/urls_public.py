from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import serve_landing_page, serve_media

urlpatterns = [
    path('landing/<str:url_path>/<str:token>/', serve_landing_page, name='serve_landing_page'),
    path('media/<path:path>', serve_media, name='serve_media'),
]

if settings.DEBUG or settings.SERVE_MEDIA_IN_PRODUCTION:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
