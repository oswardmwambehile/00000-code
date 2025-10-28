from django.urls import path
from .views import SubmitVisitVerificationView, UserSubmittedVerificationsView,SupervisorVisitVerificationsView

urlpatterns = [
    path('visits/submit-verification/', SubmitVisitVerificationView.as_view(), name='submit-visit-verification'),
    path('visits/my-submissions/', UserSubmittedVerificationsView.as_view(), name='my-submissions'),
    path('visits/my-verifications/', SupervisorVisitVerificationsView.as_view(), name='my-visit-verifications'),
]
