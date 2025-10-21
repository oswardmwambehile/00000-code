from rest_framework import serializers
from .models import Verification
from visits.models import Visit
from django.conf import settings

class VerificationSerializer(serializers.ModelSerializer):
    visit_id = serializers.PrimaryKeyRelatedField(
        queryset=Visit.objects.all(),
        source='content_object',
        write_only=True
    )
    customer_name = serializers.SerializerMethodField()
    contact_person_name = serializers.SerializerMethodField()
    meeting_type = serializers.SerializerMethodField()
    item_discussed = serializers.SerializerMethodField()
    visit_image_url = serializers.SerializerMethodField() 

    
    sent_to_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Verification
        fields = [
            'id',
            'visit_id',
            'customer_name',
            'contact_person_name',
            'meeting_type',
            'item_discussed',
            'visit_image_url',        
            'sent_to',
            'sent_to_name',
            'status',
            'message',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'created_at',
        ]
        read_only_fields = ['verified_by', 'verified_at', 'created_at', 'status']

    def get_customer_name(self, obj):
        visit = obj.content_object
        if visit and visit.company:
            return visit.company.company_name
        return None

    def get_contact_person_name(self, obj):
        visit = obj.content_object
        if visit and visit.contact_person:
            return visit.contact_person.contact_name
        return None

    def get_meeting_type(self, obj):
        visit = obj.content_object
        if visit:
            return visit.meeting_type
        return None

    def get_item_discussed(self, obj):
        visit = obj.content_object
        if visit:
            return visit.item_discussed
        return None

    def get_visit_image_url(self, obj):
        visit = obj.content_object
        if visit and visit.visit_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(visit.visit_image.url)
            return visit.visit_image.url
        return None

    def get_sent_to_name(self, obj):
        if obj.sent_to:
            return f"{obj.sent_to.first_name} {obj.sent_to.last_name}"
        return None

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return None
