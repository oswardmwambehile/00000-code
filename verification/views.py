from rest_framework import generics, permissions
from .models import Verification
from .serializers import VerificationSerializer

class SubmitVisitVerificationView(generics.CreateAPIView):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
