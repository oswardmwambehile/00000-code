# urls.py
from django.urls import path
from .views import PaymentListAll, PaymentDetailByCustomer

urlpatterns = [
    path("payments-list/", PaymentListAll.as_view(), name="payments-list"),
    path("payments-list/customer/<int:customer_id>/", PaymentDetailByCustomer.as_view(), name="payments-detail-customer"),
]
