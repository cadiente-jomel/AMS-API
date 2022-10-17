import os
import logging
from django.http.request import MultiPartParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db import IntegrityError
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import (
    generics,
    status,
    mixins,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from dotenv import load_dotenv

import jwt

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    EmailVerificationSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    UserSerializer,
    UserProfileSerializer,
    LandlordSerializer,
    TenantSerializer,
)
from users.utils import Email
from users.models import (
    User, 
    Landlord, 
    Tenant, 
    UserProfile
)
from core.permissions import (
    IsLandlordAuthenticated, 
    IsTenantAuthenticated, 
    IsUserAuthenticated, 
    IsAdministratorAuthenticated
)

load_dotenv()
logger = logging.getLogger("secondary")


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        email = Email()
        user = get_object_or_404(User, email=user_data["email"])
        access_token = RefreshToken().for_user(user).access_token
        absurl = email.get_absolute_url(access_token, request)
        body = f"Hi, {user.get_short_name} click the link below to verify your account \n {absurl}"
        data = {
            "email_body": body,
            "email_subject": "Verify Account",
            "send_to": user.email,
        }
        email.send_email(data)

        return Response(data=user_data, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(APIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=str(os.getenv("ALGORITHMS"))
            )
            user = get_object_or_404(User, id=payload["user_id"])

            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=["is_verified"])
                return Response(
                    {"message": "Account Verified"}, status=status.HTTP_200_OK
                )
        except jwt.ExpiredSignatureError as err:
            return Response(
                {"error": "Verification Token Expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.DecodeError as err:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("---viewset entry point ---")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info(f"serializer data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = (ResetPasswordEmailRequestSerializer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")

        if User.objects.filter(email=email).exists():
            user = get_object_or_404(User, email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            current_domain = get_current_site(request=request).domain
            relative_link = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            absurl = f"{request.scheme}://{current_domain}{relative_link}"

            email_body = (
                f"Hello, \n Click the link below to reset your password \n {absurl}"
            )
            data = {
                "email_body": email_body,
                "email_subject": "Reset Your Password",
                "send_to": user.email,
            }
            Email.send_email(data)
            return Response(
                {"message": "Email has been sent to your inbox."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Email not yet registered, you can sign up instead"},
            status=status.HTTP_404_NOT_FOUND,
        )


class PasswordTokenCheckAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid Token"}, status=status.HTTP_403_FORBIDDEN
                )

            return Response({"message": "Token Alive"}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as indentifier:
            return Response(
                {"error": "Invalid Token, request a new one."},
                status=status.HTTP_403_FORBIDDEN,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password changed"}, status=status.HTTP_200_OK
        )


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]

            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Logging out...")
            return Response(
                {"message": "You have been logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError as err:
            return Response(
                {"message": "Bad Token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutAllAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    @transaction.atomic()
    def post(self, request):
        try:
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            blacklisted = [BlacklistedToken(token=token) for token in tokens]
            BlacklistedToken.objects.bulk_create(blacklisted)
            return Response(
                {"message": "You have been logout to all devices."},
                status=status.HTTP_200_OK,
            )
        except IntegrityError as err:
            return Response(
                {"error": "Something went wrong while trying to logout all devices."},
                status=status.HTTP_409_CONFLICT,
            )


class UserAPIView(
    generics.GenericAPIView, 
    mixins.ListModelMixin
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministratorAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveUserProfileAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permissions_classes = [IsUserAuthenticated, ]
    parser_classes = [MultiPartParser, ]
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            instance=self.get_object(),
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["user"]
        if not validated_data == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer) -> None:
        serializer.save()


class LandlordAPIView(
    generics.GenericAPIView, 
    mixins.ListModelMixin
):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer
    permission_classes = [IsAdministratorAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RetrieveUserAPIView(
    mixins.RetrieveModelMixin, 
    generics.GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsUserAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            instance=self.get_object(),
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True) 

        validated_data = serializer.validated_data["id"]
        if not validated_data == request.user.id:
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer) -> None:
        serializer.save()


class RetrieveLandlordAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin 
):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TenantAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
):
    serializer_class = TenantSerializer
    permission_classes = [IsLandlordAuthenticated, IsAdministratorAuthenticated]

    def get_queryset(self):
        try:
            queryset = Tenant.objects.filter(
                tenantroom__room__branch__assigned_landlord=self.request.user
            )
        except Tenant.DoesNotExist as err:
            raise ValidationError(detail="Invalid parameter.")

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RetrieveTenantAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin 
):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsUserAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
