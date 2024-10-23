from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Webhook
from core.forms import WebhookForm
from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404
import json
import hmac
import hashlib
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import CampaignResult
from core.utils import generate_unique_token
from django.utils import timezone
import logging
import pytz

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def webhook_list(request):
    webhooks = Webhook.objects.filter(user=request.user)
    return render(request, 'webhook_list.html', {'webhooks': webhooks})

@login_required
def add_webhook(request):
    if request.method == 'POST':
        form = WebhookForm(request.POST)
        if form.is_valid():
            webhook = form.save(commit=False)
            webhook.user = request.user
            webhook.save()
            return redirect('webhook_list')
    else:
        form = WebhookForm()
    return render(request, 'webhook_form.html', {'form': form})

@login_required
def edit_webhook(request, webhook_id):
    webhook = get_object_or_404(Webhook, id=webhook_id, user=request.user)
    if request.method == 'POST':
        form = WebhookForm(request.POST, instance=webhook)
        if form.is_valid():
            form.save()
            messages.success(request, 'Webhook actualizado con éxito.')
            return redirect('webhook_list')
    else:
        form = WebhookForm(instance=webhook)
    return render(request, 'webhook_form.html', {'form': form})

@login_required
def delete_webhook(request, webhook_id):
    webhook = get_object_or_404(Webhook, id=webhook_id, user=request.user)
    if request.method == 'POST':
        webhook.delete()
        messages.success(request, 'Webhook eliminado con éxito.')
        return redirect('webhook_list')
    return render(request, 'webhook_confirm_delete.html', {'webhook': webhook})

@csrf_exempt
def process_webhook(request, campaign_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result_id = data.get('result_id')
            if result_id is None:
                raise ValueError("'result_id' no está presente en los datos")
            
            try:
                result = CampaignResult.objects.get(id=result_id)
            except CampaignResult.DoesNotExist:
                return HttpResponse("CampaignResult no encontrado", status=404)

            webhooks = Webhook.objects.filter(user=result.campaign.user, is_active=True)

            for webhook in webhooks:
                payload = {
                    'campaign_id': campaign_id,
                    'result_id': result.id,
                    'status': result.status,
                    'email': result.target.email,
                    'timestamp': result.updated_at.isoformat()
                }

                headers = {
                    'Content-Type': 'application/json',
                }

                if webhook.secret:
                    signature = hmac.new(
                        webhook.secret.encode(),
                        msg=json.dumps(payload).encode(),
                        digestmod=hashlib.sha256
                    ).hexdigest()
                    headers['X-Dreamphish-Signature'] = signature

                response = requests.post(webhook.url, json=payload, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Error al enviar webhook: {response.status_code} - {response.text}")

            return HttpResponse(status=200)
        except json.JSONDecodeError:
            return HttpResponse("Error al decodificar JSON", status=400)
        except Exception as e:
            return HttpResponse(str(e), status=400)
    return HttpResponse(status=405)

@csrf_exempt
def test_webhook(request, campaign_id):
    if request.method == 'GET':
        return render(request, 'test_webhook.html', {'campaign_id': campaign_id})
    elif request.method == 'POST':
        try:
            from core.models import Campaign
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Generar un token único
            token = generate_unique_token()
            
            # Crear un CampaignResult de prueba con el token único
            test_result = CampaignResult.objects.create(
                campaign=campaign,
                target=campaign.group.targets.first(),  # Asume que hay al menos un objetivo en el grupo
                status='opened',
                token=token
            )
            
            # Crear datos de prueba
            test_data = {
                'result_id': test_result.id,
                'status': 'opened',
            }
            # Convertir los datos a JSON y establecer el content_type
            request._body = json.dumps(test_data).encode('utf-8')
            request.content_type = 'application/json'
            return process_webhook(request, campaign_id)
        except Exception as e:
            return HttpResponse(str(e), status=400)
    else:
        return HttpResponse(status=405)

def send_webhook(campaign_id, result_id, event_type, email, form_data=None):
    try:
        result = CampaignResult.objects.get(id=result_id)
        campaign = result.campaign
        target = result.target
        webhooks = Webhook.objects.filter(user=campaign.user, is_active=True)

        for webhook in webhooks:
            # Determinar el timestamp correcto basado en el tipo de evento
            if event_type == 'email_opened':
                event_timestamp = result.opened_timestamp
            elif event_type == 'landing_page_opened':
                event_timestamp = result.landing_page_opened_timestamp
            else:
                event_timestamp = result.sent_timestamp

            # Si no hay timestamp específico, usar la hora actual
            if not event_timestamp:
                event_timestamp = timezone.now()

            # Asegurarse de que el timestamp esté en UTC
            event_timestamp = event_timestamp.astimezone(pytz.UTC)

            payload = {
                'campaign_id': campaign_id,
                'campaign_name': campaign.name,
                'target_id': target.id,
                'target_email': email,
                'event_type': event_type,
                'timestamp': event_timestamp.isoformat(),
                'ip_address': result.ip_address
            }
            
            if form_data:
                payload['form_data'] = form_data

            headers = {
                'Content-Type': 'application/json',
            }

            if webhook.secret:
                signature = hmac.new(
                    webhook.secret.encode(),
                    msg=json.dumps(payload).encode(),
                    digestmod=hashlib.sha256
                ).hexdigest()
                headers['X-Dreamphish-Signature'] = signature

            response = requests.post(webhook.url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"Error al enviar webhook: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Error al procesar webhook: {str(e)}")
