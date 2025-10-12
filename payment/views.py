from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Max, F, Value, DecimalField
from django.db.models.functions import Coalesce
from .models import Payment
from sales.models import Sales
from .serializers import PaymentSummarySerializer

class PaymentListAll(generics.ListAPIView):
    serializer_class = PaymentSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns aggregated payment data per customer.
        Each customer appears only once with total collected,
        remaining balance, and last payment date.
        """
        # Aggregate payments per customer
        queryset = (
            Payment.objects
            .select_related("sales__customer")
            .values(
                "sales__customer__id",
                "sales__customer__company_name",
            )
            .annotate(
                total_collected=Coalesce(Sum("amount"), Value(0, output_field=DecimalField())),
                last_payment_date=Max("created_at"),
            )
            .order_by("-last_payment_date")
        )

        # Calculate remaining balance for each customer
        result = []
        for item in queryset:
            # Get all sales for this customer
            sales_qs = Sales.objects.filter(customer_id=item["sales__customer__id"]).prefetch_related("items")

            total_price = 0
            for sale in sales_qs:
                total_price += sum(i.price or 0 for i in sale.items.all())

            item["remaining_balance"] = max(total_price - item["total_collected"], 0)
            result.append(item)

        return result
    

# views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer

class PaymentDetailByCustomer(generics.ListAPIView):
    """
    Returns all payments for a specific customer.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        if not customer_id:
            return Payment.objects.none()  # or raise 404

        return Payment.objects.filter(sales__customer_id=customer_id).order_by("-created_at")

