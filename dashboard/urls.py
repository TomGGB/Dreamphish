from django.urls import path
from . import views
from email_templates.views import email_template_list
from landing_pages.views import landing_page_list
from groups.views import group_list
from campaigns.views import campaign_list, export_campaign_results_csv, export_campaign_results
from smtp.views import smtp_list

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('email_template_list/', email_template_list, name='email_template_list'),
    path('landing_page_list/', landing_page_list, name='landing_page_list'),
    path('group_list/', group_list, name='group_list'),
    path('campaign_list/', campaign_list, name='campaign_list'),
    path('smtp_list/', smtp_list, name='smtp_list'),
    path('campaign/<int:campaign_id>/export/csv/', export_campaign_results_csv, name='export_campaign_results_csv'),
    path('campaign/<int:campaign_id>/export/', export_campaign_results, name='export_campaign_results'),
]
