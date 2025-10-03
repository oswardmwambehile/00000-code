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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Branch
from .forms import BranchForm
from django.contrib.auth import authenticate, update_session_auth_hash
from .models import Branch
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from accounts.models import User
from django.db.models import Q  # 🔍 For OR lookups


def add_visit(request):
     if request.user.is_authenticated:
        return render(request, 'users/add_vist.html')
     else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')

def dashboard(request):
    if request.user.is_authenticated:
       return render(request, 'company/dashboard.html')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


User = get_user_model()

  # Make sure you have this model

def register(request):
    if request.user.is_authenticated:
        branches = Branch.objects.all()  # Fetch all branches dynamically

        if request.method == 'POST':
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            password1 = request.POST.get('password1')
            position = request.POST.get('position')
            zone = request.POST.get('zone')
            branch_id = request.POST.get('branch')  # We'll use the ID
            contact = request.POST.get('contact')
            company_name = request.POST.get('company_name')

            # ✅ Password validations (keep your existing code)
            if password != password1:
                messages.error(request, "Passwords do not match.")
                return redirect('register')
            # ... other password checks ...

            # Check if user exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('register')

            # Validate contact
            if not re.match(r'^(?:\+255|0)[67][1-9]\d{7}$', contact):
                messages.error(request, "Enter a valid Tanzanian phone number.")
                return redirect('register')

            if User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).exists():
                messages.error(request, "A user with this first and last name already exists.")
                return redirect('register')

            # ✅ Get the branch instance from ID
            try:
                branch_instance = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                messages.error(request, "Selected branch does not exist.")
                return redirect('register')

            # Create the user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                position=position,
                zone=zone,
                branch=branch_instance,  # Save as object, not string
                contact=contact,
                company_name=company_name
            )

            messages.success(request, "User created successfully.")
            return redirect('register')

        return render(request, 'company/add_user.html', {"branches": branches})
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')


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
            if user.position in ['Facilitator', 'Product Brand Manager', 'Zonal Sales Executive','admin']:
                return redirect('dashboard')  # Redirect to 'index' for these positions
            elif user.position in ['Corporate Officer', 'Mobile Sales Officer', 'Desk Sales Officer']:
                return redirect('add_visit')  # Redirect to 'dashboard' for these positions
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
    



def branch_list(request):
    if request.user.is_authenticated:
        """
        Display all branches, handle adding new branches, and updating existing ones via modals.
        """
        branches = Branch.objects.all().order_by("-created_at")

        # Handle Add Branch
        if request.method == "POST" and "add_branch" in request.POST:
            form = BranchForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("branch-list")
        else:
            form = BranchForm()

        # Handle Update Branch
        if request.method == "POST" and "update_branch" in request.POST:
            branch_id = request.POST.get("branch_id")
            branch = get_object_or_404(Branch, pk=branch_id)
            form_update = BranchForm(request.POST, instance=branch)
            if form_update.is_valid():
                form_update.save()
                return redirect("branch-list")
        else:
            form_update = BranchForm()

        return render(
            request,
            "company/branch_list.html",
            {
                "branches": branches,
                "form": form,
                "form_update": form_update,
            }
        )
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')

# Keep detail and delete as-is
def branch_detail(request, pk):
    if request.user.is_authenticated:
        branch = get_object_or_404(Branch, pk=pk)
        return render(request, "company/branch_detail.html", {"branch": branch})
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')

def branch_delete(request, pk):
    if request.user.is_authenticated:
        branch = get_object_or_404(Branch, pk=pk)
        if request.method == "POST":
            branch.delete()
            return redirect("branch-list")
        return render(request, "company/branch_confirm_delete.html", {"branch": branch})
    
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')






def user_list(request):
    if request.user.is_authenticated:
            query = request.GET.get('q', '')
            users = User.objects.all().order_by('-date_joined')  # order by newest first

            if query:
                users = users.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(company_name__icontains=query)  # <-- added this
                ).order_by('-date_joined')  # maintain ordering after filtering

            return render(request, 'company/user_list.html', {
                'users': users,
                'query': query,
            })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
    





@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_user(request, user_id):
    if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)
            branches = Branch.objects.all()  # ✅ Fetch all branches dynamically

            if request.method == "POST":
                user.first_name = request.POST.get("first_name")
                user.last_name = request.POST.get("last_name")
                user.email = request.POST.get("email")
                user.company_name = request.POST.get("company_name")
                user.position = request.POST.get("position")
                user.zone = request.POST.get("zone")

                # ✅ Get branch instance from ID
                branch_id = request.POST.get("branch")
                try:
                    branch_instance = Branch.objects.get(id=branch_id)
                    user.branch = branch_instance
                except Branch.DoesNotExist:
                    messages.error(request, "Selected branch does not exist.")
                    return redirect("edit_user", user_id=user.id)

                user.contact = request.POST.get("contact")
                user.save()

                messages.success(request, "User updated successfully.")
                return redirect("user_list")

            return render(request, "company/edit_user.html", {
                "user_obj": user,
                "branches": branches  # ✅ pass branches to template
            })
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
    



@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def toggle_user_status(request, user_id):
    if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)

            if user == request.user:
                message = "You can't change your own status."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': message}, status=403)
                messages.error(request, message)
                return redirect('user_list')

            if user.is_superuser:
                message = "You can't change status of a superuser."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': message}, status=403)
                messages.error(request, message)
                return redirect('user_list')

            # Toggle active status
            user.is_active = not user.is_active
            user.save()

            status = "enabled" if user.is_active else "disabled"
            message = f"User {user.email} has been {status}."

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'is_active': user.is_active})

            messages.success(request, message)
            return redirect('user_list')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
    



def user_detail(request, user_id):
    if request.user.is_authenticated:
            user = get_object_or_404(User, id=user_id)

           
            context = {
                'user': user,
            }

            return render(request, 'company/user_detail.html', context)
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')





def change_password(request):
    if request.user.is_authenticated:
            if request.method == 'POST':
                current_password = request.POST.get('current_password')
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')

                if not request.user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif new_password1 != new_password2:
                    messages.error(request, 'New passwords do not match.')
                elif len(new_password1) < 8:
                    messages.error(request, 'New password must be at least 8 characters.')
                else:
                    request.user.set_password(new_password1)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # keep user logged in
                    messages.success(request, 'Password changed successfully.')
                    return redirect('change_password')

            return render(request, 'users/change_password.html')
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')





def adminchange_password(request):
     if request.user.is_authenticated:
            if request.method == 'POST':
                current_password = request.POST.get('current_password')
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')

                if not request.user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif new_password1 != new_password2:
                    messages.error(request, 'New passwords do not match.')
                elif len(new_password1) < 8:
                    messages.error(request, 'New password must be at least 8 characters.')
                else:
                    request.user.set_password(new_password1)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # keep user logged in
                    messages.success(request, 'Password changed successfully.')
                    return redirect('change_password')

            return render(request, 'company/change_password.html')
     else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')
     

def profile_view(request):
    if request.user.is_authenticated:
        user = request.user  # The logged-in user
        return render(request, 'users/profile.html', {'user': user})
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')

def adminprofile_view(request):
    if request.user.is_authenticated:
        user = request.user  # The logged-in user
        return render(request, 'company/profile.html', {'user': user})
    else:
        messages.error(request,'You must login first to access the page')
        return redirect('login')

