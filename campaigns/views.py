from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Campaign, CampaignResult, LandingPage
from core.forms import CampaignForm
from core.views import send_phishing_email
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import uuid
import csv
import json
from openpyxl import Workbook
from django.http import HttpResponse
import io
from django.conf import settings
import requests
from core.utils import generate_unique_token


@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(user=request.user)
    return render(request, 'campaign_list.html', {'campaigns': campaigns})

@login_required
def add_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, user=request.user)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            return redirect('campaign_list')
    else:
        form = CampaignForm(user=request.user)
    return render(request, 'campaign_form.html', {'form': form})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    results = CampaignResult.objects.filter(campaign=campaign)
    return render(request, 'campaign_detail.html', {'campaign': campaign, 'results': results})

@login_required
def start_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if campaign.status == 'draft':
        campaign.status = 'in_progress'
        campaign.save()
        
        current_site = get_current_site(request)
        domain = current_site.domain.split(':')[0]  # Elimina el puerto si está presente
        
        for target in campaign.group.targets.all():
            token = generate_unique_token()
            result = CampaignResult.objects.create(campaign=campaign, target=target, token=token)
            result.sent_timestamp = timezone.localtime() 
            result.save()
            
            landing_pages = campaign.landing_group.landing_pages.all()
            public_domain = domain
            if settings.PUBLIC_PORT and settings.PUBLIC_PORT != 80:
                public_domain = f"{domain}:{settings.PUBLIC_PORT}"
            landing_page_url = f"http://{public_domain}/landing/{landing_pages[0].url_path}/{token}/"
            
            email_body = campaign.email_template.body.replace('{NOMBRE}', target.first_name)
            email_body = email_body.replace('{APELLIDO}', target.last_name)
            email_body = email_body.replace('{CARGO}', target.position)
            email_body = email_body.replace('{EMAIL}', target.email)
            email_body = email_body.replace('{LINK}', landing_page_url)
            
            # Modificar los enlaces en el cuerpo del correo
            soup = BeautifulSoup(email_body, 'html.parser')
            for a in soup.find_all('a', href=True):
                a['href'] = landing_page_url
            
            # Añadir la imagen de tracking
            tracking_url = f"http://{public_domain}/track/{token}/"
            tracking_img = soup.new_tag('img', src=tracking_url, width="1", height="1", style="display:none;")
            
            # Asegurarse de que haya un cuerpo en el HTML
            if soup.body:
                soup.body.append(tracking_img)
            else:
                # Si no hay cuerpo, crear uno y añadir el contenido original y la imagen de tracking
                new_body = soup.new_tag('body')
                new_body.extend(soup.contents)
                new_body.append(tracking_img)
                soup.append(new_body)
            
            modified_email_body = str(soup)
            
            try:
                send_phishing_email(
                    campaign.smtp,
                    target.email,
                    campaign.email_template.subject,
                    modified_email_body
                )
                result.email_sent = True
                result.save()
            except Exception as e:
                messages.error(request, f'Error al enviar correo a {target.email}: {str(e)}')
        
        if CampaignResult.objects.filter(campaign=campaign, email_sent=True).exists():
            CampaignResult.status = 'email_sent'
            campaign.save()
            messages.success(request, 'Campaña iniciada. Los correos se han enviado con éxito.')
        else:
            messages.warning(request, 'No se pudo enviar ningún correo. Verifique la configuración SMTP.')
    else:
        messages.error(request, 'La campaña ya ha sido iniciada.')
    return redirect('dashboard')


@login_required
def delete_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaña eliminada con éxito.')
    return redirect('campaign_list')

@login_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaña actualizada con éxito.')
            return redirect('campaign_list')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'core/campaign_form.html', {'form': form, 'edit_mode': True})


@login_required
def export_campaign_results(request, campaign_id, format='csv'):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    results = CampaignResult.objects.filter(campaign=campaign)

    headers = ['events', 'uuid', 'email', 'first_name', 'last_name', 'work_position', 'status', 'ip_address', 'user_agent', 'post_data', 'latitude', 'longitude', 'send_date', 'reported', 'is_archived', 'created_at', 'updated_at']

    if format == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados de Campaña"
        ws.append(headers)
    else:  # CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="resultados_campana_{campaign.name}.csv"'
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

    for result in results:
        events = []
        if result.email_opened:
            events.append('Email abierto')
        if result.landing_page_opened:
            events.append('Landing page visitada')
        if result.status == 'form_submitted':
            events.append('Formulario enviado')
        
        post_data = json.loads(result.post_data) if result.post_data else {}
        post_data_str = json.dumps(post_data)

        row = [
            ', '.join(events),
            result.token,
            result.target.email,
            result.target.first_name,
            result.target.last_name,
            result.target.position,
            result.status,
            result.ip_address or '',
            result.user_agent or '',
            post_data_str,
            result.latitude or '',
            result.longitude or '',
            result.sent_timestamp.strftime('%Y-%m-%d %H:%M:%S') if result.sent_timestamp else '',
            'FALSE',
            'FALSE',
            result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result.created_at else '',
            result.updated_at.strftime('%Y-%m-%d %H:%M:%S') if result.updated_at else '',
        ]

        if format == 'excel':
            ws.append(row)
        else:  # CSV
            writer.writerow(row)

    if format == 'excel':
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="resultados_campana_{campaign.name}.xlsx"'

    return response




