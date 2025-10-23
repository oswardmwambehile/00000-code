from django.urls import path
from .views import SubmitVisitVerificationView, UserSubmittedVerificationsView,SupervisorVisitVerificationsView, SupervisorVisitVerificationDetailView, SupervisorUpdateVerificationView, UserVerificationDetailView, VerificationMessageListView, VerificationMessageCreateView, UserVerificationMessageListView, UserVerificationMessageCreateView

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

  path('visits/my-submissions/<int:verification_id>/',
    UserVerificationDetailView.as_view(),
    name='user-verification-detail'
  ),

   path(
        'verifications/<int:verification_id>/messages/',
        VerificationMessageListView.as_view(),
        name='verification-messages'
    ),
    path(
        'verifications/<int:verification_id>/messages/send/',
        VerificationMessageCreateView.as_view(),
        name='verification-send-message'
    ),



    path(
        'user-verifications/<int:verification_id>/messages/',
        UserVerificationMessageListView.as_view(),
        name='verification-messages'
    ),
    path(
        'user-verifications/<int:verification_id>/messages/send/',
        UserVerificationMessageCreateView.as_view(),
        name='verification-send-message'
    ),
]



