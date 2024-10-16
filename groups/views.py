from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Group, Target
from core.forms import GroupForm, TargetForm, TargetFormSet, ImportForm
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
import csv
import io
from django.http import JsonResponse


@login_required
def group_list(request):
    groups = Group.objects.filter(user=request.user)
    return render(request, 'group_list.html', {'groups': groups})

@login_required
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.user = request.user
            group.save()
            messages.success(request, 'Grupo añadido con éxito.')
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'group_form.html', {'form': form})

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
    return render(request, 'group_form.html', {'form': form, 'formset': formset, 'edit_mode': True})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Grupo eliminado con éxito.')
    return redirect('group_list')


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id, user=request.user)
    targets = group.targets.all()
    return render(request, 'group_detail.html', {'group': group, 'targets': targets})

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
    return render(request, 'target_form.html', {'form': form, 'group': group})

@login_required
def import_targets_from_csv(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            group_name = form.cleaned_data['group_name']
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    csv_file.seek(0)
                    decoded_file = csv_file.read().decode('iso-8859-1')
                except UnicodeDecodeError:
                    return JsonResponse({'success': False, 'error': 'No se pudo decodificar el archivo CSV.'})
            
            group = Group.objects.create(name=group_name, user=request.user)

            csv_reader = csv.reader(io.StringIO(decoded_file))
            next(csv_reader, None)  # Saltar la primera línea (encabezados)
            for row in csv_reader:
                if len(row) >= 4:
                    Target.objects.create(
                        group=group,
                        first_name=row[0],
                        last_name=row[1],
                        position=row[2],
                        email=row[3]
                    )

            return JsonResponse({'success': True})
    else:
        form = ImportForm()
    return render(request, 'import_csv.html', {'form': form})

@login_required
def delete_target(request, target_id):
    if request.method == 'POST':
        target = get_object_or_404(Target, id=target_id, group__user=request.user)
        target.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
