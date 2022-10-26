from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api.viewsets import (
    RegisterAPIView,
    VerifyEmailAPIView,
    LoginAPIView,
    LogoutAPIView,
    LogoutAllAPIView,
    RequestPasswordResetAPIView,
    PasswordTokenCheckAPIView,
    SetNewPasswordAPIView,
    RetrieveUserAPIView,
    RetrieveUserProfileAPIView,
    LandlordAPIView,
    RetrieveLandlordAPIView,
    TenantAPIView,
    RetrieveTenantAPIView,
)

app_name = "users"

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name="register"),
    path("verify-email", VerifyEmailAPIView.as_view(), name="verify-email"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
    path("logout-all/", LogoutAllAPIView.as_view(), name="logout-all"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path(
        "request-reset-password",
        RequestPasswordResetAPIView.as_view(),
        name="request-reset-email",
    ),
    path(
        "password-reset/<uidb64>/<token>",
        PasswordTokenCheckAPIView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete",
        SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path("users/<int:pk>", RetrieveUserAPIView.as_view(), name="user-detail"),
    path(
        "user-profiles/<int:pk>",
        RetrieveUserProfileAPIView.as_view(),
        name="user-profile-detail",
    ),
    path("landlords", LandlordAPIView.as_view(), name="landlord-list"),
    path(
        "landlords/<int:pk>", RetrieveLandlordAPIView.as_view(), name="landlord-detail"
    ),
    path("tenants", TenantAPIView.as_view(), name="tenant-list"),
    path("tenants/<int:pk>", RetrieveTenantAPIView.as_view(), name="tenant-detail"),
]
