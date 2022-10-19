from decimal import Decimal, getcontext
from django.utils.timezone import datetime
from django.db import models

from dateutil import relativedelta

from users.models import Tenant
from buildings.models import Room, TenantRoom
from core.models import BaseModel


from .utils import generate_transation_number

getcontext().prec = 2

class Payment(BaseModel):
    class STATUS(models.TextChoices):
        UNPAID = "up", "Unpaid"
        PAID = "pd", "Paid"
        PARTIAL = "p", "Partial"

    class TYPE(models.TextChoices):
        RENT = "R", "Rent",
        MISCELLANEOUS = "Misc", "Miscellaneous"

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS.choices, default=STATUS.UNPAID)
    type = models.CharField(max_length=15, choices=TYPE.choices, default=TYPE.RENT)
    tenant = models.ForeignKey(TenantRoom, on_delete=models.CASCADE, related_name="tenant_payments")
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Payment issued to {self.tenant.tenant.get_full_name}"
    
    @property
    def number_of_months(self) -> int:
        """ Calculate how many months have pass relative to date provided"""
        delta = relativedelta.relativedelta(self.start_date, self.end_date)
        return delta.months

    def save(self, *args, **kwargs):
        if self.status != "pd" and self.type == "R":
            self.amount = self.tenant.room.rent_price * self.number_of_months
        super(Payment, self).save(*args, **kwargs)

class Transaction(BaseModel):
    transaction_no = models.CharField(max_length=15, unique=True, editable=False, default=generate_transation_number)
    payment_received = models.DecimalField(max_digits=8, decimal_places=2)
    date_received = models.DateField()
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="payment_transactions")
    
    @property
    def remaining_balance(self) -> Decimal:
        return Decimal(self.payment.amount) - Decimal(self.payment_received)
        
    def __str__(self):
        return f"{self.transaction_no}"

