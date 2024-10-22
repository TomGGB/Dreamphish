from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from core.views import serve_landing_page, track_email_open

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('add/', views.add_campaign, name='add_campaign'),
    path('<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('<int:campaign_id>/start/', views.start_campaign, name='start_campaign'),
    path('<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('track/<str:token>/', track_email_open, name='track_email_open'),
    path('l/<str:url_path>/<str:token>/', serve_landing_page, name='serve_landing_page'),
    path('export/<int:campaign_id>/<str:format>/', views.export_campaign_results, name='export_campaign_results'),
    path('refresh/<int:campaign_id>/', views.refresh_campaign_results, name='refresh_campaign_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
