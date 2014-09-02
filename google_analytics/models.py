from django.contrib import admin
from django.contrib.sites.models import Site
from django.db import models


class Analytic(models.Model):
    site = models.ForeignKey(Site, unique=True)
    analytics_code = models.CharField(blank=True, max_length=100)
