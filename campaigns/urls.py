from django.urls import path
from . import views
from core.views import serve_landing_page, track_email_open

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('add/', views.add_campaign, name='add_campaign'),
    path('<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('<int:campaign_id>/start/', views.start_campaign, name='start_campaign'),
    path('<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('l/<str:url_path>/<str:token>/', serve_landing_page, name='serve_landing_page'),
    path('track_email_open/<str:token>/', track_email_open, name='track_email_open'),
]
