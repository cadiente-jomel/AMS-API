from typing import Dict, Any
import logging
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from users.models import (
    User,
    Tenant,
    Landlord,
    UserProfile,
)

T = Dict[str, Any]
logger = logging.getLogger("secondary")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    default_error_messages = {
        "username": _("The username should only contain alphanumeric characters.")
    }

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs: Any) -> T:
        """Enter if user enter the same password"""
        try:
            validate_password(attrs.get("password"))
        except ValidationError as err:
            return Response({"errors": err})
        if not attrs.get("username").isalnum():
            raise serializers.ValidationError(self.default_error_messages)

        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": _("Password field didn't match")}
            )
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    tokens = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["tokens"]


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        models = ["password", "uidb64", "token"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            uidb64 = attrs.get("uidb64")
            token = attrs.get("token")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise exceptions.AuthenticationFailed("The reset link is invalid", 401)

            user.set_password(password)
            user.save()

            return user
        except Exception as exc:
            raise exceptions.AuthenticationFailed("The reset link is invalid", 401)

        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    password = serializers.CharField(
        min_length=8, write_only=True, style={"input_type": "password"}
    )
    email = serializers.SerializerMethodField(read_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_email(self, obj: str) -> str:
        user = get_object_or_404(User, username=obj["username"])
        return user.email

    def get_tokens(self, obj: T) -> T:
        try:
            user = User.objects.get(username=obj["username"])
        except User.DoesNotExist as err:
            return Response(
                {
                    "error": err,
                }
            )

        return user.tokens

    class Meta:
        fields = ["email", "username", "password", "tokens"]

    def validate(self, attrs: Any) -> T:
        logger.info("---entry-point----")
        username = attrs.get("username", None)
        password = attrs.get("password", None)

        logger.info(f"username: {username} \n password: {password}")

        if username is None or password is None:
            raise exceptions.ParseError(detail=_("Required parameters not provided."))
        user_auth = authenticate(username=username, password=password)

        if not user_auth:
            raise exceptions.AuthenticationFailed(
                detail=_("Invalid credentials, Try again.")
            )
        if not user_auth.is_active:
            raise exceptions.AuthenticationFailed(
                detail=_("Account disabled, contact admin.")
            )
        if not user_auth.is_verified:
            raise exceptions.AuthenticationFailed(detail=_("Email not verified"))

        logger.info(
            f"user_auth: {user_auth} \nemail: {user_auth.email} \nusername: {user_auth.username}"
        )
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=555)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    get_full_name = serializers.ReadOnlyField()
    get_short_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "get_full_name",
            "get_short_name",
        ]
        extra_kwargs = {"url": {"view_name": "users:user-detail"}}


class TenantSerializer(serializers.HyperlinkedModelSerializer):
    get_full_name = serializers.ReadOnlyField()
    get_short_name = serializers.ReadOnlyField()

    class Meta:
        model = Tenant
        fields = [
            "url",
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "get_full_name",
            "get_short_name",
        ]
        extra_kwargs = {"url": {"view_name": "users:tenant-detail"}}


class LandlordSerializer(serializers.HyperlinkedModelSerializer):
    get_full_name = serializers.ReadOnlyField()
    get_short_name = serializers.ReadOnlyField()

    class Meta:
        model = Landlord
        fields = [
            "url",
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "get_full_name",
            "get_short_name",
        ]
        extra_kwargs = {"url": {"view_name": "users:landlord-detail"}}


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["url", "user", "address", "image", "phone"]
        extra_kwargs = {
            "url": {"view_name": "users:user-profile-detail"},
            "user": {"view_name": "users:user-detail"}
        } 
