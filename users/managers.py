from django.db import models


class TenantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role="T")


class LandlordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role="LL")
