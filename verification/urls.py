from django.urls import path
from .views import SubmitVisitVerificationView, UserSubmittedVerificationsView

urlpatterns = [
    path('visits/submit-verification/', SubmitVisitVerificationView.as_view(), name='submit-visit-verification'),
    path('visits/my-submissions/', UserSubmittedVerificationsView.as_view(), name='my-submissions'),
]
