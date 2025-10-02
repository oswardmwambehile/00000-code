from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import CustomerForm, CustomerContactForm
from .models import Customer, CustomerContact
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Customer, CustomerContact
from .forms import CustomerForm, CustomerContactForm

# Use a plain ModelFormSet for adding contacts
ContactFormSet = modelformset_factory(
    CustomerContact,
    form=CustomerContactForm,
    extra=1,          # at least one empty row
    can_delete=True
)

def add_customer(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            customer_form = CustomerForm(request.POST)
            # IMPORTANT: use the SAME prefix for GET and POST
            formset = ContactFormSet(request.POST, queryset=CustomerContact.objects.none(), prefix="contacts")

            if customer_form.is_valid() and formset.is_valid():
                # Save parent first
                customer = customer_form.save()

                # Save contacts and attach the customer
                contacts = formset.save(commit=False)
                for c in contacts:
                    c.customer = customer
                    c.save()

                # Handle deletes (if any were added then removed)
                for obj in formset.deleted_objects:
                    obj.delete()

                return redirect("customer_list")

        else:
            customer_form = CustomerForm()
            # Same prefix in GET; start with no contacts from DB
            formset = ContactFormSet(queryset=CustomerContact.objects.none(), prefix="contacts")

        return render(request, "users/add_customer.html", {
            "customer_form": customer_form,
            "formset": formset,
            "is_update": False,   # just for your heading/buttons
        })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
    




def customer_list(request):
    if request.user.is_authenticated:
            query = request.GET.get("q", "")

            customers = Customer.objects.all()

            if query:
                customers = customers.filter(
                    Q(company_name__icontains=query) |
                    Q(designation__icontains=query)
                )

            customers = customers.order_by('-created_at')

            context = {
                "customers": customers,
                "query": query,
            }

            return render(request, "users/customer_list.html", context)
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


def admincustomer_list(request):
    if request.user.is_authenticated:
            query = request.GET.get("q", "")

            customers = Customer.objects.all()

            if query:
                customers = customers.filter(
                    Q(company_name__icontains=query) |
                    Q(designation__icontains=query)
                )

            customers = customers.order_by('-created_at')

            context = {
                "customers": customers,
                "query": query,
            }

            return render(request, "company/customer_list.html", context)
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')



def update_customer(request, pk):
    if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=pk)

            # Inline formset for contacts tied to customer
            ContactFormSet = inlineformset_factory(
                Customer,
                CustomerContact,
                form=CustomerContactForm,
                extra=0,          # no blank rows by default
                can_delete=True   # allow delete
            )

            if request.method == "POST":
                customer_form = CustomerForm(request.POST, instance=customer)
                formset = ContactFormSet(request.POST, instance=customer)

                if customer_form.is_valid() and formset.is_valid():
                    customer_form.save()
                    formset.save()  # updates, deletes, and adds new
                    messages.success(request, "✅ Customer updated successfully!")
                    return redirect("customer_list")
                else:
                    print("❌ FORM ERRORS:", customer_form.errors, formset.errors)
            else:
                customer_form = CustomerForm(instance=customer)
                formset = ContactFormSet(instance=customer)

            return render(request, "users/update_customer.html", {
                "customer_form": customer_form,
                "formset": formset,
                "customer": customer,
            })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


def adminupdate_customer(request, pk):
    if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=pk)

            # Inline formset for contacts tied to customer
            ContactFormSet = inlineformset_factory(
                Customer,
                CustomerContact,
                form=CustomerContactForm,
                extra=0,          # no blank rows by default
                can_delete=True   # allow delete
            )

            if request.method == "POST":
                customer_form = CustomerForm(request.POST, instance=customer)
                formset = ContactFormSet(request.POST, instance=customer)

                if customer_form.is_valid() and formset.is_valid():
                    customer_form.save()
                    formset.save()  # updates, deletes, and adds new
                    messages.success(request, "✅ Customer updated successfully!")
                    return redirect("customer_list")
                else:
                    print("❌ FORM ERRORS:", customer_form.errors, formset.errors)
            else:
                customer_form = CustomerForm(instance=customer)
                formset = ContactFormSet(instance=customer)

            return render(request, "company/update_customer.html", {
                "customer_form": customer_form,
                "formset": formset,
                "customer": customer,
            })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')



# ✅ DELETE CUSTOMER
def delete_customer(request, pk):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, pk=pk)

        if request.method == "POST":
            customer.delete()
            messages.success(request, "🗑️ Customer deleted successfully!")
            return redirect("customer_list")

        return render(request, "users/customer_confirm_delete.html", {"customer": customer})
    
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


# ✅ DELETE CUSTOMER
def admindelete_customer(request, pk):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, pk=pk)

        if request.method == "POST":
            customer.delete()
            
            return redirect("customer_list")

        return render(request, "company/customer_confirm_delete.html", {"customer": customer})
    
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')




def view_customer(request, customer_id):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, id=customer_id)
        contacts = CustomerContact.objects.filter(customer=customer)

        return render(request, "users/customer_detail.html", {
            "customer": customer,
            "contacts": contacts,
        })
    
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')



def view_customers(request, customer_id):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, id=customer_id)
        contacts = CustomerContact.objects.filter(customer=customer)

        return render(request, "company/customer_detail.html", {
            "customer": customer,
            "contacts": contacts,
        })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
