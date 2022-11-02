import logging
from django.contrib import admin
from django.apps import apps

logger = logging.getLogger("secondary")

app = apps.get_app_config("payments")
for model in app.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRigstered as err:
        logger.info("App already registered")
# Register your models here.
