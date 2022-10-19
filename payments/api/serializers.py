from rest_framework import serializers
from payments.models import Payment, Transaction


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
            "due_date"
        ]
        extra_kwargs = {
            "url": {"view_name": "payments:payment-detail"},
            "tenant": {"view_name": "buildings:tenantroom-detail"},
        }

        def validate(self, attrs):
            start_date = attrs.get("start_date", None)
            end_date = attrs.get("end_date", None)
            type = attrs.get("type", None)

            if start_date is None or end_date is None and type  == "Misc":
                raise serializers.ValidationError("start_date and end_date fields should be empty if the payment type is 'Misc'")
            
            if start_date is None or end_date is None and type == "R":
                raise serializers.ValidationError("start_date and end_date fields can't be empty when the type is 'Rent'")

            if start_date > end_date:
                raise serializers.ValidationError("start date cannot be greater than end date.")

            return attrs
 

class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    remaining_balance = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = [
            "url",
            "id",
            "transaction_no",
            "payment_received",
            "remaining_balance",
            "date_received",
            "payment"
        ]
        extra_kwargs = {
            "url": {"view_name": "payments:transaction-detail"},
            "payment": {"view_name": "payments:payment-detail"},
        }
