from django.urls import path
from .views import SubmitVisitVerificationView

urlpatterns = [
    path('visits/submit-verification/', SubmitVisitVerificationView.as_view(), name='submit-visit-verification'),
]
