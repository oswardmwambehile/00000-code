 # sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("new-sales/", views.new_sales, name="new_sales"),
     path('sales_list/', views.sales_list, name='sales_list'),
    path("sales-detail/<int:sale_id>/", views.sales_detail, name="sales_detail"),
    path("get-contacts/<int:company_id>/", views.get_contacts, name="get_contacts"),
    path("<int:pk>/update/", views.update_sale, name="update_sale"),
    path("get-contact-details/<int:contact_id>/", views.get_contact_details, name="get_contact_details"),
    # Add other sales-related URLs here if needed
]

 
