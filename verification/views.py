from rest_framework import generics, permissions
from .models import Verification
from .serializers import VerificationSerializer
from .serializers import SupervisorUpdateVerificationSerializer

# ---------------- Submit Verification ----------------
class SubmitVisitVerificationView(generics.CreateAPIView):
    """
    Create a new verification. The logged-in user is automatically set as submitted_by.
    """
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)  # set submitter automatically

# ---------------- List Submitted Verifications ----------------
class UserSubmittedVerificationsView(generics.ListAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Verification.objects.filter(submitted_by=user).order_by('-created_at')




class SupervisorVisitVerificationsView(generics.ListAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Verification.objects.filter(sent_to=user, content_type__model='visit')





class SupervisorVisitVerificationDetailView(generics.RetrieveAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id' 

    def get_queryset(self):
        # Only allow the supervisor to view their assigned verifications
        user = self.request.user
        return Verification.objects.filter(sent_to=user, content_type__model='visit')
    

class SupervisorUpdateVerificationView(generics.UpdateAPIView):
    serializer_class = SupervisorUpdateVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id'

    def get_queryset(self):
        user = self.request.user
        return Verification.objects.filter(sent_to=user)






