from django.urls import path
from .views import (
    SubmitSalesVerificationView,
    UserSubmittedSalesVerificationsView,
    SupervisorSalesVerificationsView,
    SupervisorSalesVerificationDetailView,
    SupervisorUpdateSalesVerificationView,
    UserSalesVerificationDetailView,
    SalesVerificationMessageListView,
    SalesVerificationMessageCreateView,
    UserSalesVerificationMessageListView,
    UserSalesVerificationMessageCreateView,
)

urlpatterns = [
    # ---------------- Submit / List ----------------
    path('sales/submit-verification/', SubmitSalesVerificationView.as_view(), name='submit-sales-verification'),
    path('sales/my-verifications/', UserSubmittedSalesVerificationsView.as_view(), name='user-sales-verifications'),

    # ---------------- Supervisor Views ----------------
    path('sales/supervisor-verifications/', SupervisorSalesVerificationsView.as_view(), name='supervisor-sales-verifications'),
    path('sales/supervisor-verifications/<int:verification_id>/', SupervisorSalesVerificationDetailView.as_view(), name='supervisor-sales-verification-detail'),
    path('sales/supervisor-verifications/<int:verification_id>/update/', SupervisorUpdateSalesVerificationView.as_view(), name='supervisor-sales-verification-update'),

    # ---------------- User Detail ----------------
    path('sales/my-verifications/<int:verification_id>/', UserSalesVerificationDetailView.as_view(), name='user-sales-verification-detail'),

    # ---------------- Messages ----------------
    path('sales/verifications/<int:verification_id>/messages/', SalesVerificationMessageListView.as_view(), name='sales-verification-messages'),
    path('sales/verifications/<int:verification_id>/messages/send/', SalesVerificationMessageCreateView.as_view(), name='sales-verification-send-message'),

    path('sales/user-verifications/<int:verification_id>/messages/', UserSalesVerificationMessageListView.as_view(), name='sales-verification-messages'),
    path('sales/user-verifications/<int:verification_id>/messages/send/', UserSalesVerificationMessageCreateView.as_view(), name='sales-verification-send-message'),
]
