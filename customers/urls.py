from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer-list'),             # GET all customers
    path('customers/create/', views.customer_create, name='customer-create'),  # POST create customer
    path('customers/<int:pk>/', views.customer_detail, name='customer-detail'),# GET single customer
    path('customers/<int:pk>/update/', views.customer_update, name='customer-update'), # PUT update
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer-delete'), # DELETE
   
]

