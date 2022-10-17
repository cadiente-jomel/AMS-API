from rest_framework import serializers
from emergency_contacts.models import EmergencyContact


class EmergencyContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "url",
            "branch",
            "contact_no",
            "type",
            "other",
        ]
        extra_kwargs = {
            "url": {"view_name": "emergency_contacts:emergency-contact-detail"},
            "branch": {"view_name": "buildings:branch-detail"},
            "other": {"required": False, "allow_null": True},
            "type": {"required": False, "allow_null": True},
        }
