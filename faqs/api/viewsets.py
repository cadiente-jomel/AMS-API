import logging
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    FAQSerializer,
    AnswerSerializer,
    ConcernSerializer,
)
from faqs.models import FAQ, Answer, Concern
from users.models import (
    Landlord,
    Tenant,
    User,
)

from buildings.models import Branch

logger = logging.getLogger("secondary")
default_error_message = {
    "error": "Something went wrong, make sure to check your request."
}


class FAQAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        branch_param = self.request.query_params.get("branch", None)

        faqs = FAQ.objects.select_related("branch").filter(branch=branch_param)

        return faqs

    def get(self, request, *args, **kwargs):
        reqparams = request.query_params.get("branch", None)

        if reqparams == '""' or reqparams == "''":
            reqparams = None

        if reqparams == "" or reqparams is None:
            return Response(
                {"error": "Make sure to specify the branch"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except:
            return Response(default_error_message, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveFAQAPIView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = FAQ.objects.select_related("branch").all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AnswerAPIView(generics.GenericAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except:
            return Response(default_error_message, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveAnswerAPIView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Answer.objects.select_related("complaint_id", "answered_by").all()
    serializer_class = AnswerSerializer
    permission_classes = [
        AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ConcernAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = ConcernSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        branch = self.request.query_params.get("branch", None)

        concern = Concern.objects.select_related("complained_by").filter(
            complained_by__room__branch__id=branch
        )

        return concern

    def get(self, request, *args, **kwargs):
        reqparams = request.query_params.get("branch", None)

        if reqparams == '""' or reqparams == "''":
            reqparams = None

        if reqparams == "" or reqparams is None:
            return Response(
                {"error": "Make sure to specify the branch"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except:
            return Response(default_error_message, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveConcernAPIView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    serializer_class = ConcernSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # TODO changed this to current logged in user later.
        user = Landlord.objects.all().first()
        concern = Concern.objects.select_related("complained_by").filter(
            complained_by__room__branch__assigned_landlord=user
        )

        return concern

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)
