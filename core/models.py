from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver


class User(AbstractUser):
    api_key = models.CharField(max_length=255, unique=True)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True)
    password_change_required = models.BooleanField(default=False)
    account_locked = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',
        related_query_name='core_user',
    )

@receiver(pre_save, sender=User)
def generate_api_key(sender, instance, **kwargs):
    if not instance.api_key:
        instance.api_key = uuid.uuid4().hex

class Role(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

class Permission(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Solo auto_now_add
    def __str__(self):
        return self.name
    
class LandingGroup(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Target(models.Model):
    group = models.ForeignKey(Group, related_name='targets', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    email = models.EmailField()

class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    html = models.TextField()
    modified_date = models.DateTimeField(auto_now=True)  # Solo auto_now
    envelope_sender = models.EmailField()

class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    html = models.TextField()
    modified_date = models.DateTimeField(auto_now=True)  # Solo auto_now
    capture_credentials = models.BooleanField(default=False)
    capture_passwords = models.BooleanField(default=False)
    redirect_url = models.URLField(blank=True)

class SMTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    from_address = models.EmailField()
    ignore_cert_errors = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Solo auto_now_add
    updated_at = models.DateTimeField(auto_now=True)  # Solo auto_now
    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Solo auto_now_add
    updated_at = models.DateTimeField(auto_now=True)  # Solo auto_now
    def __str__(self):
        return self.name

class LandingPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    html_content = models.TextField()
    url_path = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    zip_file_name = models.CharField(max_length=255, blank=True, null=True)
    landing_group = models.ForeignKey(LandingGroup, on_delete=models.CASCADE, related_name='landing_pages')
    image_file_paths = models.TextField(default='[]')  # Añade esta línea

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE) # Grupo de destinatarios
    landing_group = models.ForeignKey(LandingGroup, on_delete=models.CASCADE)  # Grupo de landing pages
    smtp = models.ForeignKey(SMTP, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Solo auto_now_add
    completed_date = models.DateTimeField(null=True, blank=True)  # Sin default
    launch_date = models.DateTimeField(null=True, blank=True)  # Sin default
    send_by_date = models.DateTimeField(null=True, blank=True)  # Sin default

class CampaignResult(models.Model):
    email_sent = models.BooleanField(default=False)
    email_opened = models.BooleanField(default=False)
    landing_page_opened = models.BooleanField(default=False)
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    target = models.ForeignKey('Target', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    landing_page_opened_timestamp = models.DateTimeField(blank=True, null=True)  # Sin default
    opened_timestamp = models.DateTimeField(blank=True, null=True)  # Sin default
    sent_timestamp = models.DateTimeField(blank=True, null=True)  # Sin default
    created_at = models.DateTimeField(null=True)  # Permitir nulos temporalmente
    updated_at = models.DateTimeField(auto_now=True)  # Solo auto_now
    post_data = models.TextField(blank=True, null=True)  # Campo para almacenar los datos del formulario
    latitude = models.FloatField(blank=True, null=True)  # Para almacenar latitud
    longitude = models.FloatField(blank=True, null=True)  # Para almacenar longitud

    def __str__(self):
        return self.token

class LandingPageAsset(models.Model):
    landing_page = models.ForeignKey(LandingPage, related_name='assets', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    content = models.TextField()
    relative_path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.file_name} - {self.file_type}"