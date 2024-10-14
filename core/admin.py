from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.LandingGroup)
admin.site.register(models.LandingPage)
admin.site.register(models.Target)
admin.site.register(models.Template)
admin.site.register(models.SMTP)
admin.site.register(models.EmailTemplate)
admin.site.register(models.Group)
admin.site.register(models.Campaign)
admin.site.register(models.CampaignResult)
