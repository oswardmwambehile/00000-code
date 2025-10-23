from rest_framework import serializers
from .models import Verification, VerificationMessage
from visits.models import Visit
from visits.utils import get_location_name


# ---------------- VerificationMessage Serializer ----------------
class VerificationMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = VerificationMessage
        fields = ['id', 'sender', 'sender_name', 'message', 'created_at']
        read_only_fields = ['id', 'sender_name', 'created_at']

    def get_sender_name(self, obj):
        first = getattr(obj.sender, "first_name", "") or ""
        last = getattr(obj.sender, "last_name", "") or ""
        full_name = f"{first} {last}".strip()
        return full_name if full_name else getattr(obj.sender, "email", "")



class VerificationSerializer(serializers.ModelSerializer):
   
    messages = serializers.SerializerMethodField()  

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

    
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    place_name = serializers.SerializerMethodField()

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
            'latitude',
            'longitude',
            'place_name',
            'sent_to',
            'submitted_by_name',
            'sent_to_name',
            'status',
            'user_message',
            'supervisor_message',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'created_at',
            'messages',  
        ]
        read_only_fields = [
            'verified_by',
            'verified_by_name',
            'verified_at',
            'created_at',
            'status',
            'supervisor_message',
            'messages',
        ]

    
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

    def get_latitude(self, obj):
        visit = obj.content_object
        return visit.latitude if visit else None

    def get_longitude(self, obj):
        visit = obj.content_object
        return visit.longitude if visit else None

    def get_place_name(self, obj):
        visit = obj.content_object
        if visit and visit.latitude and visit.longitude:
            loc_data = get_location_name(visit.latitude, visit.longitude)
            return loc_data.get("place_name", "Unknown")
        return "Unknown"

    
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

    def get_messages(self, obj):
        all_messages = []

        # 1️⃣ User message (from Verification)
        if obj.user_message and obj.submitted_by:
            sender = obj.submitted_by
            sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or sender.email
            all_messages.append({
                "id": f"user-{obj.id}",
                "sender": sender.id,
                "sender_name": sender_name,
                "message": obj.user_message,
                "created_at": obj.created_at,
            })

        # 2️⃣ Chat messages
        chat_messages = VerificationMessage.objects.filter(verification=obj).order_by("created_at")
        for msg in chat_messages:
            sender = msg.sender
            sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or sender.email
            all_messages.append({
                "id": msg.id,
                "sender": sender.id,
                "sender_name": sender_name,
                "message": msg.message,
                "created_at": msg.created_at,
            })

        # 3️⃣ Supervisor message
        if obj.supervisor_message and obj.verified_by:
            sender = obj.verified_by
            sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or sender.email
            all_messages.append({
                "id": f"supervisor-{obj.id}",
                "sender": sender.id,
                "sender_name": sender_name,
                "message": obj.supervisor_message,
                "created_at": obj.verified_at,
            })

        # 4️⃣ Sort all messages chronologically
        all_messages = sorted(all_messages, key=lambda m: m["created_at"])
        return all_messages



# ---------------- Supervisor Update Serializer ----------------
class SupervisorUpdateVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['status', 'supervisor_message']
        extra_kwargs = {
            'status': {'required': True},
            'supervisor_message': {'required': False},
        }

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user:
            instance.verified_by = request.user
        return super().update(instance, validated_data)
