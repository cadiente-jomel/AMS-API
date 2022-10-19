from django.db import models
from core.models import BaseModel
from users.models import Tenant, Landlord

# Create your models here.


class Branch(BaseModel):
    class Type(models.TextChoices):
        LOW_RISE = "LRB", "Low-Rise Building"
        MID_RISE = "MRB", "Mid-Rise Building"
        HIGH_RISE = "HRB", "High-Rise Building"
        GARDEN_STYLE = "GSB", "Garden-Style Building"

    assigned_landlord = models.ForeignKey(
        Landlord, on_delete=models.CASCADE, related_name="branch_landlord"
    )
    location = models.CharField("Branch Address", max_length=250)
    branch_name = models.CharField(max_length=120, blank=True, null=True)
    number_of_rooms = models.IntegerField()
    building_type = models.CharField(max_length=30, choices=Type.choices)

    def __str__(self) -> str:
        if self.branch_name is None:
            return f"{self.location} branch"
        return f"{self.branch_name}"

    class Meta:
        verbose_name_plural = "Branches"


class Room(BaseModel):
    class Type(models.TextChoices):
        SHARED = "M", "Shared"
        SOLO = "S", "Solo"

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="branch_room"
    )
    room_no = models.IntegerField(default=1, blank=True)
    capacity = models.IntegerField(default=1, blank=True)
    type = models.CharField(
        "Room Type", max_length=10, choices=Type.choices, default=Type.SHARED
    )
    rent_price = models.DecimalField(
        default=0.00,
        max_digits=6, 
        decimal_places=2, 
        help_text="If the type is 'Shared' make sure to enter the price per head."
    )

    def __str__(self) -> str:
        if self.branch.branch_name is None:
            return f"{self.room_no} - {self.branch.location} room"
        return f"{self.room_no} - {self.branch.branch_name} room"


class TenantRoom(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="tenantroom")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"room {self.room.room_no} - {self.tenant.get_full_name}"
