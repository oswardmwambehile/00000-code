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


# -------------------------------
# Sales Detail View
# -------------------------------
@login_required
def sales_detail(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)

    context = {
        "sale": sale,
    }
    return render(request, "users/sales_detail.html", context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Sales, SalesItem
from .forms import SalesForm, UpdateSalesForm, SalesItemFormSet

def update_sale(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    customer = sale.company   # assuming Sales has ForeignKey to Customer (company)

    next_stage = request.POST.get("next_stage") or request.GET.get("next_stage")

    if request.method == "POST":
        sales_form = SalesForm(request.POST, instance=sale)
        update_form = UpdateSalesForm(request.POST, instance=sale, stage=next_stage)
        formset = SalesItemFormSet(request.POST, queryset=sale.items.all())

        if sales_form.is_valid() and update_form.is_valid() and formset.is_valid():
            sale = sales_form.save(commit=False)
            update_form = UpdateSalesForm(request.POST, instance=sale, stage=next_stage)
            sale = update_form.save()

            items = formset.save(commit=False)
            for item in items:
                item.sales = sale
                item.save()

            messages.success(request, "Sale updated successfully.")
            return redirect("sales_detail", sale.id)

    else:
        sales_form = SalesForm(instance=sale)
        update_form = UpdateSalesForm(instance=sale, stage=next_stage)
        formset = SalesItemFormSet(queryset=sale.items.all())

    return render(request, "users/update_sale.html", {
        "sale": sale,
        "customer": customer,   # ✅ add this
        "stage": customer.acquisition_stage,  # ✅ current stage from customer
        "sales_form": sales_form,
        "update_form": update_form,
        "formset": formset,
        "next_stage": next_stage,
    })
