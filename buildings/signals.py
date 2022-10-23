import calendar
from django.utils.timezone import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import TenantRoom
from payments.models import Payment

@receiver(post_save, sender=TenantRoom)
def create_payment(sender, instance, created, **kwargs) -> None:
    number_of_days = calendar.monthrange(instance.start_date.year, instance.start_date.month)[1]
    if created:
        payment = Payment(
            tenant=instance,
            start_date=instance.start_date,
            end_date=instance.start_date + timedelta(days=number_of_days), 
        )
        payment.save()
