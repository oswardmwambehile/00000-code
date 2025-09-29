from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Branch  # ✅ Changed from CustomUser to User

@admin.register(User)  # ✅ Changed from @admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):  # Class name can stay; model is now `User`
    model = User  # ✅ Changed from CustomUser to User
    list_display = (
        'email', 'first_name', 'last_name', 'company_name', 'position', 
        'zone', 'branch', 'is_staff', 'is_active'
    )
    list_filter = (
        'is_staff', 'is_active', 'company_name', 'position', 'zone', 'branch'
    )

    # Fields to display in detail/edit view
    fieldsets = (
        (_('Login Credentials'), {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'contact')}),
        (_('Company Info'), {'fields': ('company_name', 'position', 'zone', 'branch')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name', 'contact',
                'company_name', 'position', 'zone', 'branch',
                'is_staff', 'is_active'
            )
        }),
    )

    search_fields = ('email', 'first_name', 'last_name', 'contact')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
