from django.urls import path

from .api.viewsets import (
    FAQAPIView,
    RetrieveFAQAPIView,
    ConcernAPIView,
    RetrieveConcernAPIView,
    AnswerAPIView,
    RetrieveAnswerAPIView,
)

app_name = "faqs"

urlpatterns = [
    path("faqs", FAQAPIView.as_view(), name="faq"),
    path("faqs/<int:pk>", RetrieveFAQAPIView.as_view(), name="faq-detail"),
    path("concerns", ConcernAPIView.as_view(), name="concerns"),
    path("concerns/<int:pk>", RetrieveConcernAPIView.as_view(), name="concern-detail"),
    path("answers", AnswerAPIView.as_view(), name="answer"),
    path("answers/<int:pk>", RetrieveAnswerAPIView.as_view(), name="answer-detail"),
]
