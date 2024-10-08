from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import LandingPage, LandingGroup, Group, Campaign
from core.forms import LandingPageForm, CampaignForm
from django.contrib.auth.decorators import login_required
import zipfile
import os
from django.db import models
import hashlib
from django.http import JsonResponse


@login_required
def landing_page_list(request):
    landing_groups = LandingGroup.objects.all()
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
    group = get_object_or_404(LandingGroup, id=group_id)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Grupo de landing page eliminado con éxito.')
    return redirect('landing_page_list')  # O la URL que desees redirigir


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

    return render(request, 'upload_landing_page_template.html')


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