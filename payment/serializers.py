from rest_framework import serializers
from django.db.models import Sum
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    total_collected = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'customer_name',
            'amount',
            'total_collected',
            'remaining_balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        if obj.sales and obj.sales.customer:
            return obj.sales.customer.company_name
        return "Unknown Customer"

    def get_total_collected(self, obj):
        """Sum of all payments for this sale."""
        return (
            obj.sales.payments.aggregate(total=Sum('amount'))['total']
            if obj.sales else 0
        ) or 0

    def get_remaining_balance(self, obj):
        """Sale total - total collected."""
        sale_total = sum(item.price or 0 for item in obj.sales.items.all()) if obj.sales else 0
        collected = self.get_total_collected(obj)
        return sale_total - collected
    

# serializers.py
from rest_framework import serializers

class PaymentSummarySerializer(serializers.Serializer):
    sales__customer__id = serializers.IntegerField()
    sales__customer__company_name = serializers.CharField()
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_payment_date = serializers.DateTimeField()

