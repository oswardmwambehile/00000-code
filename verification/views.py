from rest_framework import generics, permissions
from .models import Verification
from .serializers import VerificationSerializer

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
