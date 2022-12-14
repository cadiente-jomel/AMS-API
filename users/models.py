# standard libraries/modules
from typing import Dict, Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from rest_framework_simplejwt.tokens import RefreshToken

# local modules
from core.models import BaseModel
from .managers import (
    TenantManager,
    LandlordManager,
)
from .utils import profile_directory_path

T = Dict[str, Any]


class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        LANDLORD = "LL", "Landlord"
        TENANT = "T", "Tenant"
        NOROLE = "NA", "NA"

    base_role = Role.NOROLE
    email = models.CharField(max_length=155, unique=True)
    role = models.CharField(max_length=150, choices=Role.choices)
    is_verified = models.BooleanField(
        "Verfied",
        help_text="Designates whether this user is verified or not.",
        default=False,
    )

    @property
    def get_full_name(self) -> str:
        try:
            return f"{self.first_name.title()} {self.last_name.title()}"
        except:
            return f"No information provided."

    @property
    def get_short_name(self) -> str:
        try:
            return f"{self.first_name.title()}"
        except:
            return f"No information provided."

    @property
    def tokens(self) -> T:
        refresh_token = RefreshToken.for_user(self)
        return {
            "refresh_token": str(refresh_token),
            "access_token": str(refresh_token.access_token),
        }

    def save(self, *args, **kwargs):
        if not self.id:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.id} -> {self.email}"


class Landlord(User):
    base_role = User.Role.LANDLORD
    objects = LandlordManager()

    class Meta:
        proxy = True


class Tenant(User):
    base_role = User.Role.TENANT
    objects = TenantManager()

    class Meta:
        proxy = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        "Profile Image",
        default="profiles/default/default.jpg",
        upload_to=profile_directory_path,
    )
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = PhoneNumberField(region="PH", blank=True, null=True)

    def save(self, *args, **kwargs) -> None:
        """adjust image resolution by (300, 300) if either of the height or width is greater than 300 pixels"""
        image = Image.open(self.image)

        if image.width > 300 or image.height > 300:
            resolution = (300, 300)
            image.thumbnail(resolution)
            image.save(self.image.path)

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.get_full_name} profile"
