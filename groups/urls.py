from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('add/', views.add_group, name='add_group'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('add-target/<int:group_id>/', views.add_target, name='add_target'),
    path('delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('edit/<int:group_id>/', views.edit_group, name='edit_group'),
    path('import_csv/', views.import_targets_from_csv, name='import_csv'),
    path('delete_target/<int:target_id>/', views.delete_target, name='delete_target'),
]
