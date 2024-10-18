from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.webhook_list, name='webhook_list'),
    path('add/', views.add_webhook, name='add_webhook'),
    path('edit/<int:webhook_id>/', views.edit_webhook, name='edit_webhook'),
    path('delete/<int:webhook_id>/', views.delete_webhook, name='delete_webhook'),
    path('test-webhook/<int:campaign_id>/', views.test_webhook, name='test_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
