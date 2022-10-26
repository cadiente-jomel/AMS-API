import logging
from rest_framework import serializers
from payments.models import Payment, Transaction

logger = logging.getLogger("secondary")


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "url",
            "id",
            "start_date",
            "end_date",
            "amount",
            "status",
            "type",
            "tenant",
            "due_date",
        ]
        extra_kwargs = {
            "url": {"view_name": "payments:payment-detail"},
            "tenant": {"view_name": "buildings:tenantroom-detail"},
            "amount": {"allow_null": True, "required": False},
        }

    def validate(self, attrs):
        logger.info("Entered validation")
        start_date = attrs.get("start_date", None)
        end_date = attrs.get("end_date", None)
        type = attrs.get("type", None)

        logger.info(
            f"variables passed\nstart_date: {start_date}\nend_date: {end_date}\ntype: {type}"
        )

        if (start_date is not None or end_date is not None) and type == "Misc":
            raise serializers.ValidationError(
                "both start_date and end_date fields should be empty if the payment type is 'Misc'"
            )

        if (start_date is None or end_date is None) and type == "R":
            raise serializers.ValidationError(
                "both start_date and end_date fields cannot be empty when the type is 'Rent'"
            )

        if type == "R":
            attrs["amount"] = 0
            if start_date > end_date:
                raise serializers.ValidationError(
                    "start date cannot be greater than end date."
                )

        return attrs


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    # remaining_balance = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = [
            "url",
            "id",
            "transaction_no",
            "payment_received",
            "date_received",
            "payment",
        ]
        extra_kwargs = {
            "url": {"view_name": "payments:transaction-detail"},
            "payment": {"view_name": "payments:payment-detail"},
            "transaction_no": {"read_only": True},
        }
