from typing import Dict, Any
import random
import string
from django.db.models import Sum


T = Dict[str, Any]


def generate_transation_number() -> str:
    """Generate id number for every transaction."""
    generated_id = "".join(
        [random.choice(string.ascii_uppercase + string.digits) for _ in range(11)]
    )
    transac_id = f"TN#{generated_id}"

    return transac_id


def calculate_payments(request, queryset, payment) -> T:
    remaining_balance = 0
    overall_total = 0
    total_payment = 0
    if queryset.count() != 0:
        total_payment = queryset.aggregate(remaining_balance=Sum("payment_received"))[
            "remaining_balance"
        ]
        if request.user.role == "T":
            payments = payment.objects.filter(tenant__tenant=request.user)
        payments = payment.objects.filter(
            tenant__room__branch__assigned_landlord=request.user
        )
        overall_total = payments.aggregate(overall_total=Sum("amount"))["overall_total"]

        remaining_balance = overall_total - total_payment

    return {
        "remaining_balance": remaining_balance,
        "overall_total": overall_total,
        "total_payment": total_payment,
    }
