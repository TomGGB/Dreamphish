from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import LandingPage, LandingGroup, Group, Campaign, LandingPageAsset
from core.forms import LandingPageForm, CampaignForm
from django.contrib.auth.decorators import login_required
import zipfile
import os
import json
from django.db import models
import hashlib
from django.http import JsonResponse
import base64
from django.conf import settings
import shutil

@login_required
def landing_page_list(request):
    landing_groups = LandingGroup.objects.filter(user=request.user)
    landing_pages_by_group = {group: group.landing_pages.all() for group in landing_groups}
    return render(request, 'landing_page_list.html', {'landing_pages_by_group': landing_pages_by_group})

@login_required
def add_landing_page(request):
    if request.method == 'POST':
        form = LandingPageForm(request.POST, request.FILES)
        if form.is_valid():
            landing_page = form.save(commit=False)
            landing_page.user = request.user
            landing_group_name = landing_page.name
            landing_group, created = LandingGroup.objects.get_or_create(name=landing_group_name, user=request.user)
            landing_page.landing_group = landing_group
            landing_page.save()
            return redirect('landing_page_list')
    else:
        form = LandingPageForm()
    return render(request, 'landing_page_form.html', {'form': form})

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
    return render(request, 'landing_page_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id, user=request.user)
    if request.method == 'POST':
        landing_page.delete()
        messages.success(request, 'Landing page eliminada con éxito.')
    return redirect('landing_page_list')

def get_landing_pages_by_group(group_id):
    group = get_object_or_404(Group, id=group_id)
    landing_pages = LandingPage.objects.filter(group=group)
    return landing_pages


@login_required
def delete_landing_group(request, group_id):
    group = get_object_or_404(LandingGroup, id=group_id, user=request.user)
    if request.method == 'POST':
        try:
            # Eliminar los recursos asociados solo para este usuario
            group_path = os.path.join(settings.MEDIA_ROOT, 'landing_pages', str(request.user.id), group.name)
            if os.path.exists(group_path):
                shutil.rmtree(group_path)
            
            # Eliminar el grupo de la base de datos
            group.delete()
            
            messages.success(request, 'Grupo de landing page y sus recursos eliminados con éxito.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el grupo de landing page: {str(e)}')
    return redirect('landing_page_list')


@login_required
def upload_landing_page_template(request):
    if request.method == 'POST':
        zip_file = request.FILES['zip_file']
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                landing_group_name = zip_file.name.replace('.zip', '')
                landing_group, created = LandingGroup.objects.get_or_create(
                    name=landing_group_name, 
                    user=request.user
                )

                max_order = LandingPage.objects.filter(landing_group=landing_group).aggregate(max_order=models.Max('order'))['max_order'] or 0

                landing_pages = {}
                assets = {}

                # Crear el directorio para el grupo de landing pages si no existe
                group_dir = os.path.join(settings.MEDIA_ROOT, 'landing_pages', str(request.user.id), landing_group_name)
                os.makedirs(group_dir, exist_ok=True)

                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue

                    file_path = file_info.filename
                    file_name = os.path.basename(file_path)
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    with zip_ref.open(file_info.filename) as file:
                        content = file.read()

                    # Guardar el archivo en el sistema de archivos
                    full_path = os.path.join(group_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'wb') as f:
                        f.write(content)

                    if file_name.startswith('index-'):
                        landing_page_name = os.path.splitext(file_name)[0]
                        base_urlpath = f'{landing_page_name}'
                        urlpath = base_urlpath
                        counter = 1

                        while LandingPage.objects.filter(url_path=urlpath).exists():
                            urlpath = f'{base_urlpath}-{counter}'
                            counter += 1

                        landing_pages[landing_page_name] = {
                            'name': landing_page_name,
                            'html_content': content.decode('utf-8', errors='ignore'),
                            'url_path': urlpath,
                            'order': int(landing_page_name.split('-')[1]) + max_order
                        }
                    else:
                        asset_type = 'css' if file_extension in ['.css'] else 'js' if file_extension in ['.js'] else 'image' if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg'] else 'font' if file_extension in ['.woff', '.woff2', '.ttf', '.eot'] else 'other'
                        assets[file_path] = {
                            'file_name': file_name,
                            'file_type': asset_type,
                            'content': base64.b64encode(content).decode('utf-8') if asset_type in ['image', 'font'] else content.decode('utf-8', errors='ignore'),
                            'relative_path': file_path
                        }

                for landing_page_name, landing_page_data in landing_pages.items():
                    landing_page = LandingPage.objects.create(
                        user=request.user,
                        landing_group=landing_group,
                        **landing_page_data
                    )

                    for asset_path, asset_data in assets.items():
                        LandingPageAsset.objects.create(
                            landing_page=landing_page,
                            **asset_data
                        )

            messages.success(request, 'Landing pages subidas con éxito.')
            return redirect('landing_page_list')

    return render(request, 'upload_landing_page_template.html')


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


