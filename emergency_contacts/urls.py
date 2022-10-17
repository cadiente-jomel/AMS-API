from django.urls import path
from .api.viewsets import (
    EmergencyContactsAPIView, 
    RetrieveEmergencyContactsAPIView
)


app_name = "emergency_contacts"

urlpatterns = [ 
    path("", EmergencyContactsAPIView.as_view(), name="emergency-contacts"),
    path("<int:pk>", RetrieveEmergencyContactsAPIView.as_view(), name="emergency-contact-detail")
]
