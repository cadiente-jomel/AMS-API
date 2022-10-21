import logging
import calendar
from decimal import Decimal, getcontext
from django.db.models import Sum
from django.utils.timezone import datetime
from django.db import models

from dateutil import relativedelta

from users.models import Tenant
from buildings.models import Room, TenantRoom
from core.models import BaseModel


from .utils import generate_transation_number

getcontext().prec = 2
logger = logging.getLogger("secondary")

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
    def number_of_months(self) -> Decimal:
        """ Calculate how many months have pass relative to date provided"""
        current_days_of_the_month = calendar.monthrange(self.end_date.year, self.end_date.month)[1]
        number_of_months =  relativedelta.relativedelta(self.end_date, self.start_date).months
        excess_days = abs(self.end_date.day - self.start_date.day) / current_days_of_the_month
        total_days = float(format(number_of_months + excess_days, '.2f'))
        logger.info(f"current_days_of_the_month: {current_days_of_the_month}")
        logger.info(f"number number_of_months: {number_of_months}")
        logger.info(f"excess days: {excess_days}")
        logger.info(f"total: {total_days}")
        return Decimal(total_days)

    def save(self, *args, **kwargs):
        if self.status != "pd" and self.type == "R":
            self.amount = self.tenant.room.rent_price * self.number_of_months
        super(Payment, self).save(*args, **kwargs)

class Transaction(BaseModel):
    transaction_no = models.CharField(max_length=15, unique=True, editable=False, default=generate_transation_number)
    payment_received = models.DecimalField(max_digits=8, decimal_places=2)
    date_received = models.DateField()
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="payment_transactions")
    
    def __str__(self):
        return f"{self.transaction_no}"

    @property
    def remaining_balance(self) -> Decimal:
        total = Transaction.objects.select_related(
            "payment"
        ).filter(payment=self.payment).aggregate(total=Sum("payment_received"))
        return Decimal(self.payment.amount) - Decimal(total['total'])
