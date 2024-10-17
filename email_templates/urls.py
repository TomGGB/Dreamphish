from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.email_template_list, name='email_template_list'),
    path('add/', views.add_email_template, name='add_email_template'),
    path('edit/<int:template_id>/', views.edit_email_template, name='edit_email_template'),
    path('delete/<int:template_id>/', views.delete_email_template, name='delete_email_template'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
