from django.contrib import admin
from .models import Sales, SalesItem

# Inline for SalesItem
class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1
    readonly_fields = ('created_at', 'updated_at')
    fields = ('product', 'price', 'created_at', 'updated_at')

# Admin for Sales
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'company_name',
        'contact_number',
        'designation',
        'status',
        'contract_outcome',
        'is_payment_collected',
        'client_budget',
        'added_by',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'contract_outcome', 'is_payment_collected', 'added_by')
    search_fields = ('company__company_name', 'contact_number', 'designation')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SalesItemInline]
    ordering = ('-created_at',)

    def company_name(self, obj):
        return obj.company.company_name if obj.company else "N/A"
    company_name.short_description = 'Company Name'

# Admin for SalesItem
@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales', 'product_name', 'price', 'created_at', 'updated_at')
    list_filter = ('sales',)
    search_fields = ('product__product__name', 'sales__company__company_name')
    readonly_fields = ('created_at', 'updated_at')

    def product_name(self, obj):
        # Access the underlying Product through ProductInterest
        return obj.product.product.name if obj.product and obj.product.product else "N/A"
    product_name.short_description = 'Product'
