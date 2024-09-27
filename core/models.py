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

    # Sobrescribe los campos de grupos y permisos con nombres relacionados únicos
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
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Target(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='targets')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    email = models.EmailField()

class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    html = models.TextField()
    modified_date = models.DateTimeField(auto_now=True)
    envelope_sender = models.EmailField()

class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    html = models.TextField()
    modified_date = models.DateTimeField(auto_now=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()  # Este campo almacenará el HTML
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class LandingPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    html_content = models.TextField()
    url_path = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE)
    smtp = models.ForeignKey(SMTP, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    launch_date = models.DateTimeField(null=True, blank=True)
    send_by_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='draft')

class CampaignResult(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='results')
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    email_sent = models.BooleanField(default=False)
    email_opened = models.BooleanField(default=False)
    link_clicked = models.BooleanField(default=False)
    landing_page_opened = models.BooleanField(default=False)
    token = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    click_timestamp = models.DateTimeField(null=True, blank=True)
    email_sent_timestamp = models.DateTimeField(null=True, blank=True)
    email_opened_timestamp = models.DateTimeField(null=True, blank=True)
    landing_page_opened_timestamp = models.DateTimeField(null=True, blank=True)


