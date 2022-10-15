from rest_framework import serializers
from faqs.models import Concern, Answer, FAQ


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "url", "complaint_id", "answered_by", "answer"]
        extra_kwargs = {
            "url": {"view_name": "faqs:answer-detail"},
            "complaint_id": {"view_name": "faqs:concern-detail"},
            "answered_by": {"view_name": "users:user-detail"},
        }


class ConcernSerializer(serializers.HyperlinkedModelSerializer):
    # answers = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name="faqs:answer-detail",
    #     source="answer_set"
    # )
    answers = AnswerSerializer(many=True, read_only=True, source="answer_set")

    class Meta:
        model = Concern
        fields = [
            "id",
            "url",
            "complaint_id",
            "complained_by",
            "title",
            "body",
            "type",
            "is_answered",
            "answers",
        ]
        extra_kwargs = {
            "complained_by": {"view_name": "buildings:tenantroom-detail"},
            "url": {"view_name": "faqs:concern-detail"},
        }


class FAQSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "url",
            "branch",
            "question",
            "answer",
            "type",
        ]

        extra_kwargs = {
            "branch": {"view_name": "buildings:branch-detail"},
            "url": {"view_name": "faqs:faq-detail"},
        }
