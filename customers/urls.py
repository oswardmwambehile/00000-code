from django.urls import path
from . import views

urlpatterns = [
   path("add/", views.add_customer, name="add_customer"),
    path("list/", views.customer_list, name="customer_list"),
    path("admin-list/", views.admincustomer_list, name="customer_lists"),
    path("delete/<int:pk>/", views.delete_customer, name="delete_customer"),
    path("admindelete/<int:pk>/", views.admindelete_customer, name="admindelete_customer"),
     path("customers/<int:pk>/update/", views.update_customer, name="update_customer"),
     path("customer/<int:pk>/update/", views.adminupdate_customer, name="updates_customer"),
     path('customers/<int:customer_id>/view/', views.view_customer, name='view_customer'),
     path('customers-view/<int:customer_id>/view/', views.view_customers, name='views_customer'),
]

