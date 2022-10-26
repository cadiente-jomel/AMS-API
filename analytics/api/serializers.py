from rest_framework import serializers
from payments.models import Transaction, Payment
from buildings.models import TenantRoom


# Total payments
#   rent payments
#   misc payments
#   by status (paid, unpaid, partial)
#  Tenant Room
# total due_date
# total tickets
#   total reports
#   total suggestions
#   total Unpaid Transaction
class AnalyticsPaymentsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    count_due_date = serializers.IntegerField()
    count_wo_due_date = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_rent_payments = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_misc_payments = serializers.DecimalField(max_digits=8, decimal_places=2)


class AnalyticsBranchSerializer(serializers.Serializer):
    count_tickets = serializers.IntegerField()
    count_answered = serializers.IntegerField()
    count_unanswered = serializers.IntegerField()


class AnalyticsTransactionSerializer(serializers.Serializer):
    count_transaction = serializers.IntegerField()


class AnalyticsOverviewSerializer(serializers.Serializer):
    pass


class AnalyticsSerializer(serializers.Serializer):
    payments = AnalyticsPaymentsSerializer()
    branch = AnalyticsBranchSerializer()
