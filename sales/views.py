# sales/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .forms import SalesForm
from products.models import ProductInterest
from django.forms import modelformset_factory
from customers.models import CustomerContact
from .models import Sales

# 🔁 Multi-product formset (same logic like visit)
ProductInterestFormSet = modelformset_factory(
    ProductInterest,
    fields=("product",),
    extra=1,
    can_delete=True
)

@login_required
def new_sales(request):
    if request.method == "POST":
        form = SalesForm(request.POST)

        if form.is_valid():
            company = form.cleaned_data.get("company")

            # 🔒 Restriction: allow only one OPEN sale per company
            if Sales.objects.filter(company=company, status="Open").exists():
                messages.error(request, f"{company} already has an open sale.")
                return render(request, "users/new_sales.html", {"form": form})

            sale = form.save(commit=False)
            sale.added_by = request.user
            sale.save()

            # Save selected product interests
            form.save_m2m()  # this saves the ManyToManyField

            messages.success(request, "Sales record created successfully!")
            return redirect("sales_list")  # Replace with your actual URL name
        else:
            print("❌ Sales form errors:", form.errors)
    else:
        form = SalesForm()

    return render(request, "users/new_sales.html", {"form": form})

# -------------------------------
# Get contacts by company_id (AJAX)
# -------------------------------
@login_required
def get_contacts(request, company_id):
    contacts = CustomerContact.objects.filter(customer_id=company_id).order_by("contact_name")
    data = [
        {
            "id": c.id,
            "contact_name": c.contact_name
        }
        for c in contacts
    ]
    return JsonResponse({"contacts": data})


# -------------------------------
# Get contact details by contact_id (AJAX)
# -------------------------------
@login_required
def get_contact_details(request, contact_id):
    contact = get_object_or_404(CustomerContact, id=contact_id)
    data = {
        "contact_number": contact.contact_detail or "",
        "designation": contact.customer.designation or ""
    }
    return JsonResponse(data)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sales


@login_required
def sales_list(request):
    """
    Display all sales records ordered by created date (newest first).
    """
    sales = Sales.objects.all().select_related(
        "company", "contact_person", "added_by"
    ).prefetch_related("product_interests").order_by("-created_at")  # newest first
    
    return render(request, "users/sales_list.html", {"sales": sales})


    # sales/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Sales

@login_required
def sales_detail(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)

    # Get products and their corresponding sales items
    products = list(sale.product_interests.all())
    items = list(sale.items.all().order_by("created_at"))

    # Pair products with items (assumes same order)
    product_items = zip(products, items)

    context = {
        "sale": sale,
        "product_items": product_items,
    }
    return render(request, "users/sales_detail.html", context)


from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Sales, SalesItem, STAGE_STATUS_MAP
from .forms import SalesForm, UpdateSalesForm, SalesItemFormSet
from payment.models import Payment

def update_sale(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    customer = sale.company
    next_stage = request.POST.get("next_stage") or request.GET.get("next_stage")
    stage_for_form = next_stage or customer.acquisition_stage

    # Ensure SalesItem exists for each product interest
    product_interests = list(sale.product_interests.all())
    existing_items = list(sale.items.all().order_by("created_at"))
    for idx, product in enumerate(product_interests):
        if idx >= len(existing_items):
            SalesItem.objects.create(sales=sale, price=Decimal("0.00"))

    sale_items = sale.items.all().order_by("created_at")

    # Formset
    formset_kwargs = {
        "queryset": sale_items,
        "prefix": "items",
        "form_kwargs": {"stage": stage_for_form},
    }
    if request.method == "POST":
        formset_kwargs["data"] = request.POST

    formset = SalesItemFormSet(**formset_kwargs)

    # Forms
    if request.method == "POST":
        sales_form = SalesForm(request.POST, instance=sale)
        update_form = UpdateSalesForm(request.POST, instance=sale, stage=stage_for_form)

        if sales_form.is_valid() and update_form.is_valid() and formset.is_valid():
            # Save main sale data
            sale = sales_form.save(commit=False)
            sale = update_form.save(commit=False)

            # Update client budget if provided
            client_budget = update_form.cleaned_data.get("client_budget")
            if client_budget is not None:
                customer.client_budget = client_budget
                customer.save()

            # Update acquisition stage if changed
            if next_stage and customer.acquisition_stage != next_stage:
                customer.acquisition_stage = next_stage
                customer.save()

            # Save items
            for item in formset.save(commit=False):
                item.sales = sale
                if item.price is not None:
                    item.price = Decimal(item.price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                item.save()
            for obj in formset.deleted_objects:
                obj.delete()

            # --- Payment Followup: Save collected amounts ---
            if next_stage == "Payment Followup":
                for idx, item in enumerate(sale.items.all(), start=1):
                    collected_str = request.POST.get(f"collected_{idx}", "0")
                    try:
                        collected = Decimal(collected_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        if collected > 0:
                            Payment.objects.create(
                                sales=sale,
                                amount=collected
                            )
                    except (InvalidOperation, ValueError):
                        continue  # skip invalid inputs

                # --- Recalculate total collected and remaining balance ---
                total_collected = sale.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                total_amount = sale.items.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
                remaining_balance = total_amount - total_collected

                # --- Update status based on remaining balance ---
                if remaining_balance <= 0:
                    sale.status = "Won Paid"
                else:
                    sale.status = "Won Pending Payment"
                sale.save()
            else:
                # --- Update status dynamically for other stages ---
                sale.update_status()

            return redirect("sales_detail", sale_id=sale.id)
        else:
            messages.error(request, "Form submission has errors.")

    else:
        sales_form = SalesForm(instance=sale)
        update_form = UpdateSalesForm(instance=sale, stage=stage_for_form)

    # --- Compute total_amount, total_collected, remaining_balance ---
    total_amount = sale.items.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
    total_collected = sale.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    remaining_balance = total_amount - total_collected

    # --- Build per-item collected mapping ---
    total_price = total_amount
    item_collected_map = {}
    for item in sale.items.all():
        proportion = item.price / total_price if total_price else 0
        item_collected_map[item.id] = (total_collected * proportion).quantize(Decimal("0.01"))

    # Pair products with formset forms for template
    product_forms = list(zip(product_interests, formset.forms))

    return render(request, "users/update_sale.html", {
        "sale": sale,
        "customer": customer,
        "stage": stage_for_form,
        "sales_form": sales_form,
        "update_form": update_form,
        "formset": formset,
        "next_stage": next_stage,
        "product_forms": product_forms,
        "total_amount": total_amount,
        "total_collected": total_collected,
        "remaining_balance": remaining_balance,
        "item_collected_map": item_collected_map,
    })
