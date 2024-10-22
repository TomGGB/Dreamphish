from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
    path('edit_target/<int:group_id>/<int:target_id>/', views.edit_target, name='edit_target'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
