from django import forms
from .models import SMTP, EmailTemplate, LandingPage, Group, Target, Campaign, LandingGroup, Webhook
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

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
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}))
    
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']

class LandingPageForm(forms.ModelForm):
    html_content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    
    class Meta:
        model = LandingPage
        fields = ['name', 'url_path', 'html_content']

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
        fields = ['name', 'smtp', 'email_template','group', 'landing_group']
        widgets = {
            'smtp': forms.Select(attrs={'class': 'form-control'}),
            'email_template': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'landing_group': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CampaignForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['smtp'].queryset = SMTP.objects.filter(user=user)
            self.fields['email_template'].queryset = EmailTemplate.objects.filter(user=user)
            self.fields['group'].queryset = Group.objects.filter(user=user)
            self.fields['landing_group'].queryset = LandingGroup.objects.filter(user=user)

class LandingPageUploadForm(forms.Form):
    name = forms.CharField(label='Nombre de la Plantilla', max_length=255)
    zip_file = forms.FileField(label='Archivo ZIP')

class ImportForm(forms.Form):
    group_name = forms.CharField(max_length=255, label='Nombre del Grupo')
    csv_file = forms.FileField(label='Archivo CSV')

class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = ['name', 'url', 'is_active', 'secret']
        widgets = {
            'secret': forms.PasswordInput(),
        }
