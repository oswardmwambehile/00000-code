# verification/serializers.py
from rest_framework import serializers
from .models import SalesVerification, SalesVerificationMessage
from sales.models import Sales
from sales.serializers import SalesSerializer  

class SalesVerificationMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = SalesVerificationMessage
        fields = ['id', 'sender', 'sender_name', 'message', 'created_at']
        read_only_fields = ['id', 'sender_name', 'created_at']

    def get_sender_name(self, obj):
        first = getattr(obj.sender, "first_name", "") or ""
        last = getattr(obj.sender, "last_name", "") or ""
        full_name = f"{first} {last}".strip()
        return full_name if full_name else getattr(obj.sender, "email", "")


class SalesVerificationSerializer(serializers.ModelSerializer):
    sale = SalesSerializer(source='content_object', read_only=True)
    customer_name = serializers.SerializerMethodField()  
    sales_id = serializers.PrimaryKeyRelatedField(
        queryset=Sales.objects.all(),
        source='content_object',
        write_only=True
    )
    status = serializers.CharField(read_only=True)
    submitted_by_name = serializers.SerializerMethodField()
    sent_to_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = SalesVerification
        fields = [
            'id',
            'sales_id',
            'sale',
            'customer_name',  
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
            'customer_name',  # <-- readonly
        ]

    # ---------------- Helper Methods ----------------
    def get_customer_name(self, obj):
        if getattr(obj.content_object, 'customer', None):
            return obj.content_object.customer.company_name          
        return None

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

        # User message
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

        # Chat messages
        chat_messages = SalesVerificationMessage.objects.filter(verification=obj).order_by("created_at")
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

        # Supervisor message
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

        return sorted(all_messages, key=lambda m: m["created_at"])


class SupervisorUpdateSalesVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesVerification
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
