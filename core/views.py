from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SMTP, EmailTemplate, LandingPage, Group, Target, Campaign, CampaignResult
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


# Create your views here.

def dashboard(request):
    campaigns = Campaign.objects.filter(user=request.user)
    selected_campaign_id = request.GET.get('campaign')
    selected_campaign = None
    results = None
    if selected_campaign_id:
        selected_campaign = get_object_or_404(Campaign, id=selected_campaign_id, user=request.user)
        results = CampaignResult.objects.filter(campaign=selected_campaign)
    return render(request, 'core/dashboard.html', {
        'campaigns': campaigns,
        'selected_campaign': selected_campaign,
        'results': results
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
    pages = LandingPage.objects.filter(user=request.user)
    return render(request, 'core/landing_page_list.html', {'pages': pages})

@login_required
def add_landing_page(request):
    if request.method == 'POST':
        form = LandingPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.user = request.user
            page.save()
            messages.success(request, 'Landing page añadida con éxito.')
            return redirect('landing_page_list')
    else:
        form = LandingPageForm()
    return render(request, 'core/landing_page_form.html', {'form': form})

def serve_landing_page(request, url_path, token):
    page = get_object_or_404(LandingPage, url_path=url_path)
    result = CampaignResult.objects.get(campaign__landing_page=page, token=token)
    result.landing_page_opened = True
    result.save()
    return HttpResponse(page.html_content)

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
    targets = group.targets.all()
    return render(request, 'core/group_detail.html', {'group': group, 'targets': targets})

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(user=request.user)
    return render(request, 'core/campaign_list.html', {'campaigns': campaigns})

@login_required
def add_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, user=request.user)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            messages.success(request, 'Campaña creada con éxito.')
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
            
            landing_page_url = request.build_absolute_uri(
                reverse('serve_landing_page', args=[campaign.landing_page.url_path, token])
            )
            
            email_body = campaign.email_template.body.replace('{NOMBRE}', target.first_name)
            email_body = email_body.replace('{APELLIDO}', target.last_name)
            email_body = email_body.replace('{PUESTO}', target.position)
            
            # Modificar los enlaces en el cuerpo del correo
            soup = BeautifulSoup(email_body, 'html.parser')
            for a in soup.find_all('a', href=True):
                a['href'] = landing_page_url
            
            # Añadir la imagen de tracking
            tracking_url = request.build_absolute_uri(reverse('track_email_open', args=[token]))
            tracking_img = soup.new_tag('img', src=tracking_url, width="1", height="1", style="display:none;")
            soup.body.append(tracking_img)
            
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
            messages.success(request, 'Campaña iniciada. Los correos se han enviado con éxito.')
        else:
            messages.warning(request, 'No se pudo enviar ningún correo. Verifique la configuración SMTP.')
    else:
        messages.error(request, 'La campaña ya ha sido iniciada.')
    return redirect('campaign_detail', campaign_id=campaign.id)

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
