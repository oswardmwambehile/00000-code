from django.urls import path
from .views import SubmitVisitVerificationView, UserSubmittedVerificationsView,SupervisorVisitVerificationsView, SupervisorVisitVerificationDetailView, SupervisorUpdateVerificationView

urlpatterns = [
    path('visits/submit-verification/', SubmitVisitVerificationView.as_view(), name='submit-visit-verification'),
    path('visits/my-submissions/', UserSubmittedVerificationsView.as_view(), name='my-submissions'),
    path('visits/my-verifications/', SupervisorVisitVerificationsView.as_view(), name='my-visit-verifications'),
    path('visits/my-verifications/<int:verification_id>/', SupervisorVisitVerificationDetailView.as_view(), name='supervisor-visit-verification-detail'),
    path(
        'visits/my-verifications/<int:verification_id>/update/',
        SupervisorUpdateVerificationView.as_view(),
        name='supervisor-update-verification'
    ),
]
