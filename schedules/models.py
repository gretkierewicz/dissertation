from django.db import models


class Schedules(models.Model):
    slug = models.SlugField(unique=True)
