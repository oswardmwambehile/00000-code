from rest_framework import serializers
from .models import Verification
from visits.models import Visit

class VerificationSerializer(serializers.ModelSerializer):
    visit_id = serializers.PrimaryKeyRelatedField(
        queryset=Visit.objects.all(),
        source='content_object',
        write_only=True
    )
    
    # Visit-related fields
    customer_name = serializers.SerializerMethodField()
    contact_person_name = serializers.SerializerMethodField()
    meeting_type = serializers.SerializerMethodField()
    item_discussed = serializers.SerializerMethodField()
    visit_image_url = serializers.SerializerMethodField() 
    
    # User-related fields
    submitted_by_name = serializers.SerializerMethodField()
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
            'submitted_by_name',
            'sent_to_name',
            'status',
            'message',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'created_at',
        ]
        read_only_fields = ['verified_by', 'verified_at', 'created_at', 'status']

    # ---------------- Visit-related methods ----------------
    def get_customer_name(self, obj):
        visit = obj.content_object
        return visit.company.company_name if visit and visit.company else None

    def get_contact_person_name(self, obj):
        visit = obj.content_object
        return visit.contact_person.contact_name if visit and visit.contact_person else None

    def get_meeting_type(self, obj):
        visit = obj.content_object
        return visit.meeting_type if visit else None

    def get_item_discussed(self, obj):
        visit = obj.content_object
        return visit.item_discussed if visit else None

    def get_visit_image_url(self, obj):
        visit = obj.content_object
        if visit and visit.visit_image:
            request = self.context.get('request')
            return request.build_absolute_uri(visit.visit_image.url) if request else visit.visit_image.url
        return None

    # ---------------- User-related methods ----------------
    def get_submitted_by_name(self, obj):
        if getattr(obj, 'submitted_by', None):
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip()
        return None

    def get_sent_to_name(self, obj):
        if getattr(obj, 'sent_to', None):
            return f"{obj.sent_to.first_name} {obj.sent_to.last_name}".strip()
        return None

    def get_verified_by_name(self, obj):
        if getattr(obj, 'verified_by', None):
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}".strip()
        return None
    

class SupervisorUpdateVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['status', 'message']
        extra_kwargs = {
            'status': {'required': True},
            'message': {'required': False},
        }

    def update(self, instance, validated_data):
        # Automatically set verified_by as the current user
        request = self.context.get('request')
        if request and request.user:
            instance.verified_by = request.user
        return super().update(instance, validated_data)

