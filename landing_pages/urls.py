from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_list, name='landing_page_list'),
    path('add/', views.add_landing_page, name='add_landing_page'),
    path('edit/<int:landing_page_id>/', views.edit_landing_page, name='edit_landing_page'),
    path('delete/<int:landing_page_id>/', views.delete_landing_page, name='delete_landing_page'),
    path('deletelandinggroup/<int:group_id>/', views.delete_landing_group, name='delete_landing_group'),
    path('upload_landing_page_template/', views.upload_landing_page_template, name='upload_landing_page_template'),
    path('preview/<int:landing_page_id>/', views.preview_landing_page, name='preview_landing_page'),
]
