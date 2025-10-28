# urls.py
from django.urls import path
from .views import PaymentListAll, PaymentDetailByCustomer, AdminPaymentListAll

urlpatterns = [
    path("payments-list/", PaymentListAll.as_view(), name="payments-list"),
    path("admin-payments-list/", AdminPaymentListAll.as_view(), name="admin-payments-list"),
    path("payments-list/customer/<int:customer_id>/", PaymentDetailByCustomer.as_view(), name="payments-detail-customer"),
]
