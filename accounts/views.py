from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re


def add_visit(request):
    return render(request, 'users/add_vist.html')


User = get_user_model()

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        position = request.POST.get('position')
        zone = request.POST.get('zone')
        branch = request.POST.get('branch')
        contact = request.POST.get('contact')
        company_name = request.POST.get('company_name')  # ✅ New

        # Password validation...
        if password != password1:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register')
        if not re.search(r'[A-Z]', password):
            messages.error(request, "Password must contain at least one uppercase letter.")
            return redirect('register')
        if not re.search(r'[a-z]', password):
            messages.error(request, "Password must contain at least one lowercase letter.")
            return redirect('register')
        if not re.search(r'\d', password):
            messages.error(request, "Password must contain at least one digit.")
            return redirect('register')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, "Password must contain at least one special character.")
            return redirect('register')

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        if not re.match(r'^(?:\+255|0)[67][1-9]\d{7}$', contact):
            messages.error(request, "Enter a valid Tanzanian phone number (e.g. +255712345678 or 0712345678).")
            return redirect('register')

        if User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).exists():
            messages.error(request, "A user with this first and last name already exists.")
            return redirect('register')

        # ✅ Create user with company_name
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            position=position,
            zone=zone,
            branch=branch,
            contact=contact,
            company_name=company_name  # ✅ Include here
        )

        messages.success(request, "User created successfully.")
        return redirect('register')

    return render(request, 'company/add_user.html')


# The POSITION_CHOICES tuple
POSITION_CHOICES = [
    ('Head of Sales', 'Head of Sales'),
    ('Facilitator', 'Facilitator'),
    ('Product Brand Manager', 'Product Brand Manager'),
    ('Corporate Manager', 'Corporate Manager'),
    ('Corporate Officer', 'Corporate Officer'),
    ('Zonal Sales Executive', 'Zonal Sales Executive'),
    ('Mobile Sales Officer', 'Mobile Sales Officer'),
    ('Desk Sales Officer', 'Desk Sales Officer'),
    ('Admin', 'Admin'),
]


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate with email as username (because USERNAME_FIELD = 'email')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Check user's position and redirect accordingly
            if user.position in ['Facilitator', 'Product Brand Manager', 'Zonal Sales Executive']:
                return redirect('add_visit')  # Redirect to 'index' for these positions
            elif user.position in ['Corporate Officer', 'Mobile Sales Officer', 'Desk Sales Officer']:
                return redirect('dashboard')  # Redirect to 'dashboard' for these positions
            else:
                return redirect('index')  # Default redirect for all other positions
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    # Handle GET request: Render the login page/form
    return render(request, 'auth/login.html')  # Ensure you have a 'login.html' template


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
