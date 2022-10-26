from django.db import transaction
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response


class DestroyInstanceMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Model instance deleted."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as err:
            return Response(
                {"message": "Model instance does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @transaction.atomic()
    def perform_destroy(self, instance):
        instance.delete()
