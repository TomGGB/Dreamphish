from django.urls import path
from . import views

urlpatterns = [
    path('', views.smtp_list, name='smtp_list'),
    path('add/', views.add_smtp, name='add_smtp'),
    path('test/<int:smtp_id>/', views.test_smtp, name='test_smtp'),
    path('edit/<int:smtp_id>/', views.edit_smtp, name='edit_smtp'),
    path('delete/<int:smtp_id>/', views.delete_smtp, name='delete_smtp'),
]
