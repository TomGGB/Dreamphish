from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Campaign, CampaignResult
import json

# Create your views here.
@login_required
def dashboard(request):
    campaigns = Campaign.objects.filter(user=request.user)
    selected_campaign_id = request.GET.get('campaign')
    print(f"Selected campaign ID: {selected_campaign_id}")  # Logging para depuración
    
    selected_campaign = None
    results = None
    chart_data = []
    
    if selected_campaign_id:
        try:
            selected_campaign = Campaign.objects.get(id=selected_campaign_id, user=request.user)
            print(f"Found campaign: {selected_campaign.name}")  # Logging para depuración
            results = CampaignResult.objects.filter(campaign=selected_campaign)
            
            # Preparar datos para el gráfico
            total_targets = results.count()
            emails_sent = results.filter(email_sent=True).count()
            emails_opened = results.filter(email_opened=True).count()
            landing_pages_opened = results.filter(landing_page_opened=True).count()
            
            chart_data = [
                {"label": "Objetivos Totales", "y": 100, "full": 100},
                {"label": "Correos Enviados", "y": round((emails_sent / total_targets) * 100, 2) if total_targets > 0 else 0, "full": 100},
                {"label": "Correos Abiertos", "y": round((emails_opened / total_targets) * 100, 2) if total_targets > 0 else 0, "full": 100},
                {"label": "Interacciones con Landing Page", "y": round((landing_pages_opened / total_targets) * 100, 2) if total_targets > 0 else 0, "full": 100}
            ]
        except Campaign.DoesNotExist:
            print(f"Campaign with ID {selected_campaign_id} not found")  # Logging para depuración

    # Cargar post_data como un diccionario
    if results:
        for result in results:
            if result.post_data:
                result.post_data = json.loads(result.post_data)  # Cargar los datos como un diccionario

    context = {
        'campaigns': campaigns,
        'selected_campaign': selected_campaign,
        'results': results,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'dashboard.html', context)
