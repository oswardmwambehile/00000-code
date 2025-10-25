from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from .models import Sales
from .serializers import SalesSerializer
from visits.models import Visit
from payment.models import Payment
from django.db import transaction  
from products.models import ProductInterest  
from decimal import Decimal


class CreateSalesFromVisit(generics.CreateAPIView):
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sales.objects.filter(added_by=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        visit_id = self.kwargs.get("visit_id")
        if not visit_id:
            raise serializers.ValidationError({"visit": "Visit ID is required in URL."})

        try:
            visit = Visit.objects.get(id=visit_id)
        except Visit.DoesNotExist:
            raise serializers.ValidationError({"visit": f"Visit with id {visit_id} does not exist."})

        items_data = self.request.data.get("items", [])
        is_order_final = self.request.data.get("is_order_final", False)
        status = self.request.data.get("status", None)
        reason_lost = self.request.data.get("reason_lost", None)


        for item in items_data:
            product_interest_id = item.get("product_interest")
            entered_price = Decimal(str(item.get("price", 0)))

            if not product_interest_id:
                continue  

            try:
                product_interest = ProductInterest.objects.select_related("product").get(id=product_interest_id)
                product_price = Decimal(str(product_interest.product.price))
            except ProductInterest.DoesNotExist:
                raise serializers.ValidationError({
                    "items": f"ProductInterest with id {product_interest_id} does not exist."
                })

            if entered_price > product_price:
                raise serializers.ValidationError({
                    "price": f"Entered price ({entered_price}) cannot be greater than product price ({product_price})."
                })

       
        existing_sale = Sales.objects.filter(
            customer=visit.company,
            added_by=self.request.user
        ).first()

        if existing_sale:
            update_data = {
                "items": items_data
            }

            if "is_order_final" in self.request.data:
                update_data["is_order_final"] = is_order_final
            if status:
                update_data["status"] = status
            if reason_lost:
                update_data["reason_lost"] = reason_lost

            serializer.instance = existing_sale
            serializer.update(existing_sale, update_data)
            sale = existing_sale
        else:
            sale = serializer.save(
                customer=visit.company,
                added_by=self.request.user,
                is_order_final=is_order_final,
                items=items_data,
                status=status if status else "Open",
                reason_lost=reason_lost,
            )

        # ⚡ Handle acquisition stage
        if visit.company.acquisition_stage not in ["Closing", "Payment Followup"]:
            if any(float(item.get("price", 0)) > 0 for item in items_data):
                visit.company.acquisition_stage = "Proposal or Negotiation"

        if visit.company.acquisition_stage == "Closing" or status in ["Lost", "Won", "Paid"]:
            visit.company.acquisition_stage = "Closing"

        # ⚡ Handle payments
        payments_input = self.request.data.get("payments", [])
        total_sale_price = sum(Decimal(item.get("price", 0)) for item in items_data)
        total_paid_so_far = sum(Decimal(p.amount) for p in sale.payments.all())

        for pay_item in payments_input:
            amount = pay_item.get("amount")
            if amount is None:
                continue

            try:
                amount = Decimal(str(amount))
            except:
                raise serializers.ValidationError({"amount": "Invalid payment amount."})

            remaining = total_sale_price - total_paid_so_far
            if amount > remaining:
                raise serializers.ValidationError(
                    {"amount": f"Cannot pay more than remaining balance ({remaining})."}
                )

            Payment.objects.create(sales=sale, amount=amount)
            visit.company.acquisition_stage = "Payment Followup"
            total_paid_so_far += amount

        # ✅ Update sale status if fully paid
        if total_paid_so_far >= total_sale_price and total_sale_price > 0:
            sale.status = "Paid"
            sale.save()
            if not payments_input:
                visit.company.acquisition_stage = "Closing"

        visit.company.save()
        return sale




from rest_framework import generics, permissions
from .models import Sales
from .serializers import SalesSerializer
from django.db.models import Sum, F

class SalesListView(generics.ListAPIView):
    """
    Returns all sales added by the logged-in user with related items, 
    customers, and totals, excluding those with total price = 0.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SalesSerializer

    def get_queryset(self):
        user = self.request.user  
        return (
            Sales.objects
            .select_related("customer", "added_by")
            .prefetch_related("items__product", "product_interests")
            .annotate(total_price_calc=Sum(F("items__price")))
            .filter(total_price_calc__gt=0, added_by=user)  
            .order_by("-created_at")
        )



class AdminSalesListView(generics.ListAPIView):
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SalesSerializer

    def get_queryset(self):
        user = self.request.user
        return (
            Sales.objects
            .select_related("customer", "added_by")
            .prefetch_related("items__product", "product_interests")
            .annotate(total_price_calc=Sum(F("items__price")))
            .filter(total_price_calc__gt=0) 
            .exclude(added_by=user)           
            .order_by("-created_at")
        )




class SalesDetailView(generics.RetrieveAPIView):
   
    queryset = (
        Sales.objects.select_related("customer", "added_by")
        .prefetch_related("items__product", "product_interests")
    )
    serializer_class = SalesSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class AdminSalesDetailView(generics.RetrieveAPIView):
    queryset = (
        Sales.objects.select_related("customer", "added_by")
        .prefetch_related("items__product", "product_interests")
    )
    serializer_class = SalesSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

