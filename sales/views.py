from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from django.db.models import Sum
from visits.models import Visit
from sales.models import Sales, SalesItem
from payment.models import Payment
from django.contrib import messages

def make_sales_order(request, visit_id):
    if request.user.is_authenticated:
            visit = get_object_or_404(Visit, id=visit_id)

            # Ensure Sales record exists
            if not visit.sales:
                sale = Sales.objects.create(company=visit.company, added_by=request.user)
                if hasattr(visit.company, "product_interests"):
                    sale.product_interests.set(visit.company.product_interests.all())
                visit.sales = sale
                visit.save()
            else:
                sale = visit.sales

            products = sale.product_interests.all()

            # Clean orphan items
            SalesItem.objects.filter(sales=sale, product__isnull=True).delete()

            # Create missing items
            existing_ids = set(SalesItem.objects.filter(sales=sale).values_list("product_id", flat=True))
            for product in products:
                if product.id not in existing_ids:
                    SalesItem.objects.create(sales=sale, product=product, price=0.0)

            queryset = SalesItem.objects.filter(sales=sale).order_by("id")
            SalesItemFormSet = modelformset_factory(SalesItem, fields=("price",), extra=0)

            items_with_payment_info = []
            for item in sale.items.all():
                total_paid = item.payments.aggregate(total=Sum("amount"))["total"] or 0
                remaining = (item.price or 0) - total_paid
                items_with_payment_info.append({
                    "item": item,
                    "total_paid": total_paid,
                    "remaining": remaining,
                })

            if request.method == "POST":
                formset = SalesItemFormSet(request.POST, queryset=queryset)
                contract_outcome = request.POST.get("contract_outcome")
                is_payment_collected = request.POST.get("is_payment_collected")
                reason_lost = request.POST.get("reason_lost", "")
                is_final_order = request.POST.get("is_final_order") == "on"

                if formset.is_valid():
                    formset.save()

                    # ===== Closing Stage Logic =====
                    if is_final_order and contract_outcome == "Won":
                        # Save newly collected payments first
                        for obj in items_with_payment_info:
                            item = obj["item"]
                            collected_value = request.POST.get(f"collected_{item.id}")
                            if collected_value:
                                collected_value = float(collected_value)
                                if collected_value > 0:
                                    Payment.objects.create(
                                        sales=sale,
                                        sales_item=item,
                                        amount=collected_value,
                                    )

                        # ===== NEW: Closing stage when fully paid manually selected =====
                        if is_payment_collected == "Yes-Full":
                            sale.status = "Won Paid"
                            if sale.company:
                                sale.company.acquisition_stage = "Closing"
                                sale.company.save()

                        else:
                            # ===== Fixed: Determine payment status automatically =====
                            total_amount = sale.items.aggregate(total=Sum("price"))["total"] or 0
                            total_collected = sale.payments.aggregate(total=Sum("amount"))["total"] or 0
                            remaining_balance = total_amount - total_collected

                            # ✅ FIX: use strict positive check for remaining balance
                            if remaining_balance > 0:
                                sale.status = "Won Pending Payment"
                                if sale.company:
                                    sale.company.acquisition_stage = "Payment Followup"
                                    sale.company.save()
                            else:
                                sale.status = "Won Paid"
                                if sale.company:
                                    sale.company.acquisition_stage = "Payment Followup"
                                    sale.company.save()

                        sale.contract_outcome = contract_outcome
                        sale.reason_lost = reason_lost
                        sale.is_order_final = True
                        sale.save()

                    # ===== Proposal / Non-final Orders =====
                    elif not is_final_order and sale.items.exists():
                        if sale.company:
                            sale.company.acquisition_stage = "Proposal or Negotiation"
                            sale.company.save()

                    elif not sale.items.exists():
                        if sale.company:
                            sale.company.acquisition_stage = "Qualifying"
                            sale.company.save()

                    return redirect("visit_detail", visit_id=visit.id)
            else:
                formset = SalesItemFormSet(queryset=queryset)

            # Totals
            total_amount = sale.items.aggregate(total=Sum("price"))["total"] or 0
            total_collected = sale.payments.aggregate(total=Sum("amount"))["total"] or 0
            remaining_balance = total_amount - total_collected

            stage = visit.company.acquisition_stage if visit.company else "Proposal or Negotiation"
            show_payment_followup_only = stage == "Payment Followup"
            show_closing = stage in ["Closing", "Payment Followup", "Completed"] or (stage == "Proposal or Negotiation" and sale.is_order_final)

            return render(request, "users/make_sales_order.html", {
                "visit": visit,
                "sales": sale,
                "formset": formset,
                "form_product_pairs": [(form, form.instance.product) for form in formset.forms],
                "stage": stage,
                "total_amount": total_amount,
                "total_collected": total_collected,
                "remaining_balance": remaining_balance,
                "show_closing": show_closing,
                "show_payment_followup_only": show_payment_followup_only,
                "items_with_payment_info": items_with_payment_info,
            })
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")

