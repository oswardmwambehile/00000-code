from rest_framework import serializers
from .models import Sales, SalesItem
from products.models import ProductInterest
from payment.models import Payment
from django.db import models


class SalesItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product.name', read_only=True)

    class Meta:
        model = SalesItem
        fields = ['id', 'product', 'product_name', 'price']


class SalesSerializer(serializers.ModelSerializer):
    items = SalesItemSerializer(many=True, required=False)
    total_price = serializers.SerializerMethodField(read_only=True)
    remaining_balance = serializers.SerializerMethodField(read_only=True)
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.first_name', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Sales
        fields = [
            'id', 'customer', 'customer_name', 'status', 'is_order_final',
            'reason_lost', 'items', 'total_price', 'added_by_name', 'created_at',
            'remaining_balance'
        ]

    # -----------------------------
    # Total Price
    # -----------------------------
    def get_total_price(self, obj):
        return sum(item.price or 0 for item in obj.items.all())

    # -----------------------------
    # Remaining Balance
    # -----------------------------
    def get_remaining_balance(self, obj):
        total_paid = obj.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        total_price = self.get_total_price(obj)
        return total_price - total_paid

    # -----------------------------
    # Create
    # -----------------------------
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sale = Sales.objects.create(**validated_data)

        for item in items_data:
            product_id = item.get('product')
            price = item.get('price', 0)

            if not ProductInterest.objects.filter(id=product_id).exists():
                raise serializers.ValidationError(
                    {"product": f"ProductInterest with id {product_id} not found."}
                )

            SalesItem.objects.create(
                sales=sale,
                product_id=product_id,
                price=price
            )
        return sale

    # -----------------------------
    # Update
    # -----------------------------
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        new_status = validated_data.get('status', instance.status)
        reason_lost = validated_data.get('reason_lost', None)

        # Prevent update if sale already Paid
        if instance.status == "Paid":
            raise serializers.ValidationError("Cannot update a sale that is already Paid.")

        # Require reason if Lost
        if new_status == "Lost" and not reason_lost:
            raise serializers.ValidationError({"reason_lost": "Reason is required when sale is lost."})

        # Update basic fields
        instance.status = new_status
        instance.reason_lost = reason_lost or instance.reason_lost
        instance.is_order_final = validated_data.get('is_order_final', instance.is_order_final)
        instance.save()

        # Update or create items
        for item_data in items_data:
            product_id = item_data.get('product')
            price = item_data.get('price', 0)

            if not ProductInterest.objects.filter(id=product_id).exists():
                raise serializers.ValidationError(
                    {"product": f"ProductInterest with id {product_id} not found."}
                )

            sales_item, _ = SalesItem.objects.get_or_create(
                sales=instance, product_id=product_id
            )
            sales_item.price = price
            sales_item.save()

        # Update acquisition stage
        remaining_balance = self.get_remaining_balance(instance)

        if new_status == "Won":
            instance.customer.acquisition_stage = "Closing"
            instance.customer.save()

        if new_status == "Won" and remaining_balance <= 0:
            instance.status = "Paid"
            instance.save()
            instance.customer.acquisition_stage = "Payment Followup"
            instance.customer.save()

        return instance
