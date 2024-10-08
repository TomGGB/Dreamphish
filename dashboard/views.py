from django.shortcuts import render
from django.shortcuts import get_object_or_404
from core.models import Campaign, CampaignResult
import json

# Create your views here.
def dashboard(request):
    # Lógica para obtener campañas y resultados
    campaigns = Campaign.objects.filter(user=request.user)
    selected_campaign_id = request.GET.get('campaign')
    selected_campaign = None
    results = None
    chart_data = []
    
    if selected_campaign_id:
        selected_campaign = get_object_or_404(Campaign, id=selected_campaign_id, user=request.user)
        results = CampaignResult.objects.filter(campaign=selected_campaign)
        
        # Preparar datos para el gráfico
        total_targets = results.count()
        emails_sent = results.filter(email_sent=True).count()
        emails_opened = results.filter(email_opened=True).count()
        landing_pages_opened = results.filter(landing_page_opened=True).count()
        
        chart_data = [
            {"y": total_targets, "label": "Objetivos Totales", "filter": "all"},
            {"y": emails_sent, "label": "Correos Enviados", "filter": "sent"},
            {"y": emails_opened, "label": "Correos Abiertos", "filter": "opened"},
            {"y": landing_pages_opened, "label": "Interacciones con Landing Page", "filter": "interacted"}
        ]
    
    # Cargar post_data como un diccionario
    if results:
        for result in results:
            if result.post_data:
                result.post_data = json.loads(result.post_data)  # Cargar los datos como un diccionario

    return render(request, 'dashboard.html', {
        'campaigns': campaigns,
        'selected_campaign': selected_campaign,
        'results': results,
        'chart_data': chart_data,
        'post_data': [result.post_data for result in results] if results else []  # Agrega los datos del formulario
    })
