from django import forms
from .models import SMTP, EmailTemplate, LandingPage, Group, Target, Campaign
from django.forms import inlineformset_factory

class SMTPForm(forms.ModelForm):
    class Meta:
        model = SMTP
        fields = ['name', 'host', 'port', 'username', 'password', 'from_address', 'ignore_cert_errors']
        widgets = {
            'password': forms.PasswordInput(),
        }

class TestSMTPForm(forms.Form):
    test_email = forms.EmailField(label='Correo de prueba')

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']

class LandingPageForm(forms.ModelForm):
    class Meta:
        model = LandingPage
        fields = ['name', 'html_content', 'url_path']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['first_name', 'last_name', 'position', 'email']

TargetFormSet = inlineformset_factory(Group, Target, form=TargetForm, extra=1, can_delete=True)

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'group', 'email_template', 'landing_page', 'smtp']
