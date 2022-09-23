from django.db import models

from core.models import BaseModel
from buildings.models import Branch, TenantRoom
from users.models import Landlord

from .utils import generate_complaint_id


class FAQ(BaseModel):
    class QuestionType(models.TextChoices):
        PAYMENT = "PI", "Payment Inquiry"
        ROOM = "RI", "ROOM INQUIRY"
        OTHER = "OTHER", "OTHER FAQs"

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=500)
    type = models.CharField(
        "Question Type", choices=QuestionType.choices, max_length=30
    )

    def __str__(self) -> str:
        return f"{self.question}"


class Concern(BaseModel):
    class ConcernType(models.TextChoices):
        PAYMENT = 'Payment', 'Payment Concern'
        ROOM = 'Room', 'Room Concern'
        SUGGESTION = 'Suggestion', 'Suggestion'
        OTHER = 'Other', 'Other Concern'


    complaint_id = models.CharField(
        max_length=50, unique=True, editable=False, default=generate_complaint_id
    )
    complained_by = models.ForeignKey(TenantRoom, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=500)
    type = models.CharField("Concern Type", max_length=50, choices=ConcernType.choices)
    is_answered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title}"

class Answer(BaseModel):
    complaint_id = models.ForeignKey(Concern, on_delete=models.CASCADE)
    answered_by = models.ForeignKey(Landlord, null=True, on_delete=models.SET_NULL)
    answer = models.CharField(max_length=500)
