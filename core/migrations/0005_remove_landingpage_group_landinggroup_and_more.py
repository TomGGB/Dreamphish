# Generated by Django 5.1.1 on 2024-10-07 18:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_landingpage_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='landingpage',
            name='group',
        ),
        migrations.CreateModel(
            name='LandingGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='landingpage',
            name='landing_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='landing_pages', to='core.landinggroup'),
            preserve_default=False,
        ),
    ]