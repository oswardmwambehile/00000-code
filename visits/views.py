# visits/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import NewVisitForm
from sales.models import Sales

@login_required
def new_visit(request, sale_id):
    # Get the related sales record
    sale = get_object_or_404(Sales, id=sale_id)

    if request.method == "POST":
        form = NewVisitForm(request.POST, request.FILES)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.sales = sale           # tie visit to this sales record
            visit.added_by = request.user
            visit.status = "Open"        # default status
            visit.save()

            messages.success(request, f"Visit for sale #{sale.id} created successfully!")
            return redirect("user_visits")
        else:
            print("❌ Visit form errors:", form.errors)
    else:
        form = NewVisitForm()

    return render(request, "users/new_visit.html", {"form": form, "sale": sale})



# visits/views.py
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


@login_required
def user_visits(request):
    """
    Display all visits added by the logged-in user with location info.
    """
    visits = Visit.objects.filter(added_by=request.user).order_by('-created_at')

    # Add location info to each visit
    for visit in visits:
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
        'visits': visits
    }
    return render(request, 'users/user_visits.html', context)


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

@login_required
def visit_detail(request, visit_id):
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

