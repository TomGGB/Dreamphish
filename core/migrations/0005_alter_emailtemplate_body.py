# Generated by Django 5.1.1 on 2024-10-17 09:48

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_landinggroup_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='body',
            field=tinymce.models.HTMLField(),
        ),
    ]
