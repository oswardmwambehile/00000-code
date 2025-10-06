 # sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('make_order/<int:visit_id>/', views.make_sales_order, name="make_sales_order"),
]

 
