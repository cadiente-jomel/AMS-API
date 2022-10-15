from django.contrib import admin
from .models import (
    Answer,
    Concern,
    FAQ,
)


admin.site.register(Answer)
admin.site.register(Concern)
admin.site.register(FAQ)
