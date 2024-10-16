from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import EmailTemplate
from core.forms import EmailTemplateForm
from django.contrib.auth.decorators import login_required
from django import forms

# Create your views here.

@login_required
def email_template_list(request):
    templates = EmailTemplate.objects.filter(user=request.user)
    return render(request, 'email_template_list.html', {'templates': templates})

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
    return render(request, 'email_template_form.html', {'form': form})

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
    return render(request, 'email_template_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id, user=request.user)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Plantilla de correo eliminada con éxito.')
    return redirect('email_template_list')

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        }
