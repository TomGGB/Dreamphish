from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import SMTP
from core.forms import SMTPForm, TestSMTPForm
from django.contrib.auth.decorators import login_required
import smtplib
from email.mime.text import MIMEText

@login_required
def smtp_list(request):
    smtps = SMTP.objects.filter(user=request.user)
    return render(request, 'smtp_list.html', {'smtps': smtps})

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
    return render(request, 'smtp_form.html', {'form': form})

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
    return render(request, 'smtp_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_smtp(request, smtp_id):
    smtp = get_object_or_404(SMTP, id=smtp_id, user=request.user)
    if request.method == 'POST':
        smtp.delete()
        messages.success(request, 'Perfil SMTP eliminado con éxito.')
    return redirect('smtp_list')