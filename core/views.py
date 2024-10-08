from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SMTP, EmailTemplate, LandingPage, Group, Target, Campaign, CampaignResult, LandingGroup
from .forms import SMTPForm, TestSMTPForm, EmailTemplateForm, LandingPageForm, GroupForm, TargetForm, CampaignForm, TargetFormSet
import smtplib
from email.mime.text import MIMEText
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
import uuid
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from bs4 import BeautifulSoup
import re
from django.templatetags.static import static
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_GET
from django.utils import timezone
import csv
import io
import pandas as pd
from django.http import HttpResponse
from .models import CampaignResult
from django.views.decorators.csrf import csrf_exempt
import json
import os
import zipfile
from django.core.files.storage import FileSystemStorage
from .forms import LandingPageUploadForm
from django.utils.text import slugify
import hashlib
from django.http import Http404
from django.db import models



def dashboard(request):
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

    return render(request, 'core/dashboard.html', {
        'campaigns': campaigns,
        'selected_campaign': selected_campaign,
        'results': results,
        'chart_data': chart_data,
        'post_data': [result.post_data for result in results] if results else []  # Agrega los datos del formulario
    })

@login_required
def smtp_list(request):
    smtps = SMTP.objects.filter(user=request.user)
    return render(request, 'core/smtp_list.html', {'smtps': smtps})

@login_required
def add_smtp(request):
    if request.method == 'POST':
        form = SMTPForm(request.POST)
        if form.is_valid():
            smtp = form.save(commit=False)
            smtp.user = request.user
            smtp.save()
            messages.success(request, 'Perfil SMTP añadido con éxito.')
            return redirect('smtp_list')
    else:
        form = SMTPForm()
    return render(request, 'core/smtp_form.html', {'form': form})

@login_required
def test_smtp(request, smtp_id):
    smtp = get_object_or_404(SMTP, id=smtp_id, user=request.user)
    if request.method == 'POST':
        form = TestSMTPForm(request.POST)
        if form.is_valid():
            test_email = form.cleaned_data['test_email']
            try:
                server = smtplib.SMTP(smtp.host, smtp.port, timeout=30)
                server.starttls()
                server.login(smtp.username, smtp.password)
                
                msg = MIMEText('Este es un correo de prueba desde DreamPhish.')
                msg['Subject'] = 'Prueba de SMTP'
                msg['From'] = smtp.from_address
                msg['To'] = test_email
                
                server.send_message(msg)
                server.quit()
                messages.success(request, f'Correo de prueba enviado con éxito a {test_email}')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo de prueba: {str(e)}')
        else:
            messages.error(request, 'Por favor, proporcione un correo válido.')
    return redirect('smtp_list')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def edit_smtp(request, smtp_id):
    smtp = SMTP.objects.get(id=smtp_id)
    if request.method == 'POST':
        form = SMTPForm(request.POST, instance=smtp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil SMTP actualizado con éxito.')
            return redirect('smtp_list')
    else:
        form = SMTPForm(instance=smtp)
    return render(request, 'core/smtp_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_smtp(request, smtp_id):
    smtp = get_object_or_404(SMTP, id=smtp_id, user=request.user)
    if request.method == 'POST':
        smtp.delete()
        messages.success(request, 'Perfil SMTP eliminado con éxito.')
    return redirect('smtp_list')

@login_required
def email_template_list(request):
    templates = EmailTemplate.objects.filter(user=request.user)
    return render(request, 'core/email_template_list.html', {'templates': templates})

@login_required
def add_email_template(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, 'Plantilla de correo añadida con éxito.')
            return redirect('email_template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'core/email_template_form.html', {'form': form})

@login_required
def landing_page_list(request):
    landing_groups = LandingGroup.objects.all()  # Obtener todos los grupos de landing pages
    landing_pages_by_group = {group: group.landing_pages.all() for group in landing_groups}  # Agrupar landing pages por grupo

    return render(request, 'core/landing_page_list.html', {
        'landing_pages_by_group': landing_pages_by_group,
    })

@login_required
def add_landing_page(request):
    if request.method == 'POST':
        form = LandingPageForm(request.POST, request.FILES)
        if form.is_valid():
            landing_page = form.save(commit=False)
            
            # Asignar el usuario actual a la landing page
            landing_page.user = request.user
            
            # Crear un nuevo LandingGroup basado en el nombre de la plantilla
            landing_group_name = landing_page.name
            landing_group, created = LandingGroup.objects.get_or_create(name=landing_group_name, user=request.user)
            
            # Asignar el LandingGroup a la LandingPage
            landing_page.landing_group = landing_group
            landing_page.save()
            
            return redirect('landing_page_list')  # Redirigir a la lista de landing pages
    else:
        form = LandingPageForm()

    return render(request, 'core/landing_page_form.html', {'form': form})

@csrf_exempt
@login_required
def serve_landing_page(request, url_path, token):
    # Obtén la landing page usando el url_path
    page = get_object_or_404(LandingPage, url_path=url_path)

    # Cambia la consulta para obtener el CampaignResult
    result = get_object_or_404(CampaignResult, token=token, campaign__landing_group=page.landing_group)

    if request.method == 'POST':
        # Capturar los datos del formulario
        form_data = request.POST.dict()


        
        # Actualizar los campos del resultado existente
        if result.post_data:
            existing_data = json.loads(result.post_data)
            existing_data.update(form_data)  # Agregar nuevos datos al diccionario existente
            result.post_data = json.dumps(existing_data)  # Convertir de nuevo a JSON

        else:
            result.post_data = json.dumps(form_data)

        # Actualizar otros campos si es necesario
        result.landing_page_opened = True
        result.landing_page_opened_timestamp = timezone.localtime()
        result.status = 'landing_page_opened'
        result.ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
        result.user_agent = request.META.get('HTTP_USER_AGENT', '')

        result.save()  # Guardar los cambios en el resultado existente

        # Verificar si hay una siguiente página
        next_page = LandingPage.objects.filter(landing_group=page.landing_group, order=page.order + 1).first()
        if next_page:
            return redirect('serve_landing_page', url_path=next_page.url_path, token=token)

    # Verificar si la landing page ya ha sido abierta
    if not result.landing_page_opened:
        result.landing_page_opened = True
        result.landing_page_opened_timestamp = timezone.localtime()
        result.status = 'landing_page_opened'
        public_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        if not public_ip:
            public_ip = request.META.get('REMOTE_ADDR', '')
        result.ip_address = public_ip
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        result.user_agent = user_agent
        result.save()

    # Modificar el contenido HTML de la landing page
    soup = BeautifulSoup(page.html_content, 'html.parser')
    form = soup.find('form')
    if form:
        form['action'] = request.build_absolute_uri(reverse('serve_landing_page', args=[url_path, token]))

    return HttpResponse(str(soup))

@login_required
def group_list(request):
    groups = Group.objects.filter(user=request.user)
    return render(request, 'core/group_list.html', {'groups': groups})

@login_required
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        formset = TargetFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            group = form.save(commit=False)
            group.user = request.user
            group.save()
            formset.instance = group
            formset.save()
            messages.success(request, 'Grupo y objetivos añadidos con éxito.')
            return redirect('group_list')
    else:
        form = GroupForm()
        formset = TargetFormSet()
    return render(request, 'core/group_form.html', {'form': form, 'formset': formset})

@login_required
def add_target(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    if request.method == 'POST':
        form = TargetForm(request.POST)
        if form.is_valid():
            target = form.save(commit=False)
            target.group = group
            target.save()
            messages.success(request, 'Objetivo añadido con éxito.')
            return redirect('group_detail', group_id=group.id)
    else:
        form = TargetForm()
    return render(request, 'core/target_form.html', {'form': form, 'group': group})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    targets = group.targets.all()  # Cambia esto si usas 'targets' como related_name
    return render(request, 'core/group_detail.html', {'group': group, 'targets': targets})

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(user=request.user)
    return render(request, 'core/campaign_list.html', {'campaigns': campaigns})

@login_required
def add_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, user=request.user)  # Asegúrate de pasar el usuario
        if form.is_valid():
            campaign = form.save(commit=False)  # No guardar aún
            campaign.user = request.user  # Establecer el usuario
            campaign.save()  # Ahora guarda la campaña
            return redirect('campaign_list')
    else:
        form = CampaignForm(user=request.user)
    return render(request, 'core/campaign_form.html', {'form': form})

@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    results = CampaignResult.objects.filter(campaign=campaign)
    return render(request, 'core/campaign_detail.html', {'campaign': campaign, 'results': results})

@login_required
def start_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if campaign.status == 'draft':
        campaign.status = 'in_progress'
        campaign.save()
        
        current_site = get_current_site(request)
        domain = current_site.domain
        
        for target in campaign.group.targets.all():
            token = generate_unique_token()
            result = CampaignResult.objects.create(campaign=campaign, target=target, token=token)
            result.sent_timestamp = timezone.localtime() 
            result.save()
            
            landing_pages = campaign.landing_group.landing_pages.all()
            landing_page_url = request.build_absolute_uri(reverse('serve_landing_page', args=[landing_pages[0].url_path, token]))
            
            email_body = campaign.email_template.body.replace('{NOMBRE}', target.first_name)
            email_body = email_body.replace('{APELLIDO}', target.last_name)
            email_body = email_body.replace('{CARGO}', target.position)
            email_body = email_body.replace('{LINK}', landing_page_url)
            
            # Modificar los enlaces en el cuerpo del correo
            soup = BeautifulSoup(email_body, 'html.parser')
            for a in soup.find_all('a', href=True):
                a['href'] = landing_page_url
            
            # Añadir la imagen de tracking
            tracking_url = request.build_absolute_uri(reverse('track_email_open', args=[token]))
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

def generate_unique_token():
    return str(uuid.uuid4())

def send_phishing_email(smtp_config, to_email, subject, body):
    try:
        from_email = smtp_config.from_address
        with smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=30) as server:
            server.starttls()
            server.login(smtp_config.username, smtp_config.password)
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Importance'] = 'High'  # Marcar el correo como importante
            msg['X-Priority'] = '1'  # Prioridad alta (1 es la más alta, 5 la más baja)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"Error al enviar correo: {str(e)}")

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        formset = TargetFormSet(request.POST, instance=group)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Grupo actualizado con éxito.')
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
        formset = TargetFormSet(instance=group)
    return render(request, 'core/group_form.html', {'form': form, 'formset': formset, 'edit_mode': True})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Grupo eliminado con éxito.')
    return redirect('group_list')

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

@require_GET
def track_email_open(request, token):
    try:
        result = CampaignResult.objects.get(token=token)
        if not result.email_opened:
            result.email_opened = True
            result.opened_timestamp = timezone.localtime()
            result.status = 'opened'  # Actualiza el estado a 'opened'
            result.save()
    except CampaignResult.DoesNotExist:
        pass
    
    # Devuelve una imagen de 1x1 píxel transparente
    return HttpResponse(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B', content_type='image/gif')

@login_required
def edit_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id, user=request.user)
    if request.method == 'POST':
        form = LandingPageForm(request.POST, instance=landing_page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Landing page actualizada con éxito.')
            return redirect('landing_page_list')
    else:
        form = LandingPageForm(instance=landing_page)
    return render(request, 'core/landing_page_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id, user=request.user)
    if request.method == 'POST':
        landing_page.delete()
        messages.success(request, 'Landing page eliminada con éxito.')
    return redirect('landing_page_list')

@login_required
def edit_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id, user=request.user)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plantilla de correo actualizada con éxito.')
            return redirect('email_template_list')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'core/email_template_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id, user=request.user)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Plantilla de correo eliminada con éxito.')
    return redirect('email_template_list')

import csv
import io
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Group, Target

@login_required
def import_targets_from_csv(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        csv_file = request.FILES.get('csv_file')

        if not group_name:
            return JsonResponse({'status': 'error', 'message': 'El nombre del grupo es obligatorio.'})

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo debe ser un CSV.')
            return JsonResponse({'status': 'error', 'message': 'El archivo debe ser un CSV.'})

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        next(io_string)  # Saltar el encabezado

        # Crear el grupo
        group = Group.objects.create(name=group_name, user=request.user)

        # Leer el CSV y crear los objetivos
        for row in csv.reader(io_string, delimiter=','):
            if len(row) < 4:
                continue  # O maneja el error de alguna manera
            first_name, last_name, position, email = row
            Target.objects.create(group=group, first_name=first_name, last_name=last_name, position=position, email=email)

        messages.success(request, 'Grupo y objetivos importados con éxito.')
        return redirect('group_list')

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@login_required
def export_campaign_results(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    results = CampaignResult.objects.filter(campaign=campaign)

    # Crear la respuesta HTTP con el tipo de contenido CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="resultados_campana_{campaign.name}.csv"'

    writer = csv.writer(response)
    # Escribir la cabecera del CSV
    writer.writerow(['events', 'uuid', 'email', 'first_name', 'last_name', 'work_position', 'status', 'ip_address', 'user_agent', 'post_data', 'latitude', 'longitude', 'send_date', 'reported', 'is_archived', 'created_at', 'updated_at'])

    for result in results:
        writer.writerow([
            '',  # events (puedes agregar lógica para esto si es necesario)
            result.token,  # uuid
            result.target.email,
            result.target.first_name,
            result.target.last_name,
            result.target.position,
            result.status,  # status
            result.ip_address,
            result.user_agent,
            result.post_data,
            '',  # latitude
            '',  # longitude
            result.sent_timestamp,  # send_date
            'FALSE',  # reported
            'FALSE',  # is_archived
            result.created_at,  # created_at
            result.updated_at,  # updated_at
        ])

    return response

@login_required
def export_campaign_results_csv(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    results = CampaignResult.objects.filter(campaign=campaign)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="resultados_campana_{campaign.name}.csv"'

    writer = csv.writer(response)
    writer.writerow(['events', 'uuid', 'email', 'first_name', 'last_name', 'work_position', 'status', 'ip_address', 'user_agent', 'post_data', 'latitude', 'longitude', 'send_date', 'reported', 'is_archived', 'created_at', 'updated_at'])

    for result in results:
        writer.writerow([
            '',  # events (puedes agregar lógica para esto si es necesario)
            result.token,  # uuid
            result.target.email,
            result.target.first_name,
            result.target.last_name,
            result.target.position,
            result.status,  # status
            result.ip_address,
            result.user_agent,
            result.post_data,
            '',  # latitude
            '',  # longitude
            result.sent_timestamp,  # send_date
            'FALSE',  # reported
            'FALSE',  # is_archived
            result.created_at,  # created_at
            result.updated_at,  # updated_at
        ])

    return response

@login_required
def upload_landing_page_template(request):
    if request.method == 'POST':
        zip_file = request.FILES['zip_file']
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                landing_group_name = zip_file.name.replace('.zip', '')
                landing_group, created = LandingGroup.objects.get_or_create(name=landing_group_name, user=request.user)

                # Obtener el máximo valor de order existente
                max_order = LandingPage.objects.filter(landing_group=landing_group).aggregate(max_order=models.Max('order'))['max_order'] or 0

                for extracted_file in zip_ref.namelist():
                    if extracted_file.endswith('.html'):
                        landing_page_name = os.path.splitext(os.path.basename(extracted_file))[0]
                        
                        with zip_ref.open(extracted_file) as file:
                            html_content = file.read().decode('utf-8')

                        # Generar un url_path único
                        base_urlpath = f'{landing_page_name}'
                        urlpath = base_urlpath
                        counter = 1

                        # Verificar unicidad del url_path
                        while LandingPage.objects.filter(url_path=urlpath).exists():
                            urlpath = f'{base_urlpath}-{counter}'
                            counter += 1

                        # Crear la LandingPage con el nuevo orden
                        landing_page = LandingPage(
                            user=request.user,
                            name=landing_page_name,
                            html_content=html_content,
                            url_path=urlpath,
                            landing_group=landing_group,
                            order=max_order + 1  # Asignar el siguiente orden
                        )
                        landing_page.save()

                        # Incrementar el max_order para la próxima landing page
                        max_order += 1

            return redirect('landing_page_list')

    return render(request, 'core/upload_landing_page_template.html')

@login_required
def view_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id, user=request.user)

    # Lógica para mostrar el contenido del índice actual
    return render(request, 'core/view_landing_page.html', {'landing_page': landing_page})

@login_required
def next_index(request, landing_page_id):
    current_page = get_object_or_404(LandingPage, id=landing_page_id, user=request.user)
    next_page = LandingPage.objects.filter(order__gt=current_page.order, user=request.user).order_by('order').first()

    if next_page:
        return redirect('view_landing_page', landing_page_id=next_page.id)
    else:
        messages.info(request, 'No hay más índices disponibles.')
        return redirect('landing_page_list')

def generate_short_hash(value):
    hash_object = hashlib.sha1(value.encode())
    return hash_object.hexdigest()[:8]  # Tomar los primeros 8 caracteres

def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect('campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignForm(instance=campaign)

    return render(request, 'core/campaign_form.html', {'form': form, 'campaign': campaign})

def get_landing_pages_by_group(group_id):
    group = get_object_or_404(Group, id=group_id)
    landing_pages = LandingPage.objects.filter(group=group)
    return landing_pages


def delete_landing_group(request, group_id):
    group = get_object_or_404(LandingGroup, id=group_id)
    group.landing_pages.all().delete()  # Eliminar todas las landing pages asociadas
    group.delete()  # Eliminar el grupo
    messages.success(request, 'Grupo de landing pages eliminado con éxito.')
    return redirect('landing_page_list')

