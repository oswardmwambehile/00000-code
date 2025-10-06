
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.dateparse import parse_date
from .models import Visit
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import VisitForm
from .models import Visit
from customers.models import CustomerContact
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Visit
from .forms import VisitForm
from sales.models import Sales, SalesItem

from django.shortcuts import render, redirect
from django.contrib import messages

from visits.models import Visit
from visits.forms import VisitForm


def new_visit(request):
    if request.user.is_authenticated:
            if request.method == "POST":
                form = VisitForm(request.POST, request.FILES)
                if form.is_valid():
                    company = form.cleaned_data.get("company")  # adjust if your field name differs

                    # ✅ Check if visit already exists for this company
                    existing_visit = Visit.objects.filter(company=company).first()

                    if existing_visit:
                        added_by_name = existing_visit.added_by.get_full_name() or existing_visit.added_by.username
                        messages.error(
                            request,
                            f"A visit for {company} already exists and it was visited by {added_by_name}."
                        )
                        # ✅ Stay on the same page (no redirect)
                        return render(request, "users/new_visit.html", {"form": form})

                    # ✅ Save new visit if it doesn't exist
                    visit = form.save(commit=False)
                    visit.added_by = request.user
                    visit.save()

                    messages.success(request, "Visit created successfully!")
                    return redirect("all_visit_list")

                else:
                    print("❌ Form errors:", form.errors)

            else:
                form = VisitForm()

            return render(request, "users/new_visit.html", {"form": form})
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")



def get_contacts(request, company_id):
    if request.user.is_authenticated:
        contacts = CustomerContact.objects.filter(customer_id=company_id).order_by("contact_name")
        data = [{"id": c.id, "contact_name": c.contact_name} for c in contacts]
        return JsonResponse({"contacts": data})
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")


def get_contact_details(request, contact_id):
    if request.user.is_authenticated:
        contact = get_object_or_404(CustomerContact, id=contact_id)
        data = {
            "contact_number": contact.contact_detail or "",  # use contact_detail
            "designation": contact.customer.designation or ""  # use the related Customer's designation
        }
        return JsonResponse(data)
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")





def get_location_name(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
            "addressdetails": 1
        }
        headers = {"User-Agent": "my_visits_app_ando_2025"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "address" in data:
                addr = data["address"]
                return {
                    "place_name": data.get("display_name", "Unknown"),
                    "region": addr.get("state", ""),
                    "zone": addr.get("county", ""),
                    "nation": addr.get("country", ""),
                }
    except Exception as e:
        print(f"Reverse geocode error: {e}")
    return {"place_name": "Unknown", "region": "", "zone": "", "nation": ""}


def all_visit_list(request):
    if request.user.is_authenticated:
            created_date = request.GET.get("created_date")
            visits_qs = Visit.objects.filter(added_by=request.user).order_by("-created_at")

            # Filter by date if provided
            if created_date:
                parsed_date = parse_date(created_date)
                if parsed_date:
                    visits_qs = visits_qs.filter(created_at__date=parsed_date)

            # Pagination
            paginator = Paginator(visits_qs, 20)
            page_number = request.GET.get("page")
            visits_page = paginator.get_page(page_number)

            # Add reverse geocode info
            for visit in visits_page:
                if visit.latitude and visit.longitude:
                    loc = get_location_name(visit.latitude, visit.longitude)
                    visit.place_name = loc["place_name"]
                    visit.region = loc["region"]
                    visit.zone = loc["zone"]
                    visit.nation = loc["nation"]
                else:
                    visit.place_name = "Not Available"
                    visit.region = ""
                    visit.zone = ""
                    visit.nation = ""

            return render(
                request,
                "users/visit_list.html",
                {
                    "visits": visits_page,
                    "created_date": created_date,
                },
            )
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Visit
import requests

def get_location_name(lat, lon):
    """
    Reverse geocode latitude and longitude using OpenStreetMap Nominatim API.
    Returns a dict with place_name, region, zone, nation.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "addressdetails": 1}
        headers = {"User-Agent": "my_visits_app_ando_2025"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "address" in data:
                addr = data["address"]
                return {
                    "place_name": data.get("display_name", "Unknown"),
                    "region": addr.get("state", ""),
                    "zone": addr.get("county", ""),
                    "nation": addr.get("country", ""),
                }
    except Exception as e:
        print(f"Reverse geocode error: {e}")
    return {"place_name": "Unknown", "region": "", "zone": "", "nation": ""}



def user_visits(request):
    if request.user.is_authenticated:
        """
        Display all visits added by the logged-in user with location info
        and user details (added_by).
        """
        visits = Visit.objects.filter(added_by=request.user).select_related('added_by', 'company', 'contact_person', 'sales').order_by('-created_at')

        for visit in visits:
            # Add location info
            if visit.latitude and visit.longitude:
                loc = get_location_name(visit.latitude, visit.longitude)
                visit.place_name = loc["place_name"]
                visit.region = loc["region"]
                visit.zone = loc["zone"]
                visit.nation = loc["nation"]
            else:
                visit.place_name = "Not Available"
                visit.region = ""
                visit.zone = ""
                visit.nation = ""

            # Add user details (who added the visit)
            if visit.added_by:
                visit.user_full_name = visit.added_by.get_full_name() or visit.added_by.username
                visit.user_email = visit.added_by.email
            else:
                visit.user_full_name = "Unknown"
                visit.user_email = "Unknown"

        context = {
            'visits': visits,
            'current_user': request.user,  # info about logged-in user
        }
        return render(request, 'users/user_visits.html', context)
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Visit
import requests

def get_location_name(lat, lon):
    """
    Reverse geocode latitude and longitude using OpenStreetMap Nominatim API.
    Returns a dict with place_name, region, zone, nation.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "addressdetails": 1}
        headers = {"User-Agent": "my_visits_app_ando_2025"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "address" in data:
                addr = data["address"]
                return {
                    "place_name": data.get("display_name", "Unknown"),
                    "region": addr.get("state", ""),
                    "zone": addr.get("county", ""),
                    "nation": addr.get("country", ""),
                }
    except Exception as e:
        print(f"Reverse geocode error: {e}")
    return {"place_name": "Unknown", "region": "", "zone": "", "nation": ""}


def visit_detail(request, visit_id):
    if request.user.is_authenticated:
            """
            Display the details of a single visit, including location info.
            """
            visit = get_object_or_404(Visit, id=visit_id)

            # Get location info
            if visit.latitude and visit.longitude:
                loc = get_location_name(visit.latitude, visit.longitude)
                visit.place_name = loc["place_name"]
                visit.region = loc["region"]
                visit.zone = loc["zone"]
                visit.nation = loc["nation"]
            else:
                visit.place_name = "Not Available"
                visit.region = ""
                visit.zone = ""
                visit.nation = ""

            context = {
                'visit': visit
            }
            return render(request, 'users/visit_detail.html', context)
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")





def visit_update(request, pk):
    if request.user.is_authenticated:
            visit = get_object_or_404(Visit, pk=pk)
            show_sales_fields = False  # Flag to reveal sales items

            # Ensure Sales record exists
            if not visit.sales and visit.company:
                sale = Sales.objects.create(company=visit.company, added_by=request.user)
                if hasattr(visit.company, "product_interests"):
                    sale.product_interests.set(visit.company.product_interests.all())
                    # Create SalesItems for all products
                    for product in sale.product_interests.all():
                        SalesItem.objects.get_or_create(sales=sale, product=product, defaults={"price": 0.0})
                visit.sales = sale
                visit.save()

            # Show sales fields if there are any products
            if visit.sales and visit.sales.items.exists():
                show_sales_fields = True

            if request.method == "POST":
                form = VisitForm(request.POST, request.FILES, instance=visit)
                action = request.POST.get("action")

                if form.is_valid():
                    visit = form.save(commit=False)

                    if visit.sales:
                        client_budget = form.cleaned_data.get("client_budget")
                        product_interests = form.cleaned_data.get("product_interests")
                        visit.sales.client_budget = client_budget
                        if product_interests:
                            visit.sales.product_interests.set(product_interests)
                        visit.sales.save()

                        # ✅ Update the Customer's acquisition_stage
                        if visit.company:
                            if client_budget:
                                visit.company.acquisition_stage = "Qualifying"
                            else:
                                visit.company.acquisition_stage = "Prospecting"
                            visit.company.save()

                    visit.save()
                    messages.success(request, "Visit updated successfully.")
                    return redirect(reverse("visit_detail", kwargs={"visit_id": visit.id}))
                else:
                    messages.error(request, "Please correct the errors below.")
            else:
                form = VisitForm(instance=visit)

            return render(request, "users/visit_update.html", {
                "form": form,
                "visit": visit,
                "show_sales_fields": show_sales_fields,
            })
    else:
        messages.error(request, "You must login first to access the page")
        return redirect("login")
