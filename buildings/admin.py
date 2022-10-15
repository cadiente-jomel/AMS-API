from django.contrib import admin
from .models import (
    Branch,
    Room,
    TenantRoom,
)

admin.site.register(Branch)
admin.site.register(Room)
admin.site.register(TenantRoom)
