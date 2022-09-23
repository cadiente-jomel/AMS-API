# standard libraries/modules
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# local modules
from core.models import BaseModel
from buildings.models import Branch

# Create your models here.
class EmergencyContact(BaseModel):
    class EmergencyNo(models.TextChoices):
        POLICE_STATION = "PS", "Police Station"
        FIRE_STATION = "FS", "Fire Station"
        AMBULANCE = "A", "Ambulance"
        LANDLORD = "LL", "Landlord"

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    contact_no = PhoneNumberField(region="PH", blank=True, null=True)
    type = models.CharField(
        "Emergency Number", max_length=30, choices=EmergencyNo.choices
    )
    other = models.CharField("Other Number", max_length=150, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.type} contanct information for {self.branch.location} branch"
