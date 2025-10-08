from rest_framework import generics, permissions
from .models import Visit
from .serializers import VisitUpdateSerializer, VisitSerializer

class VisitCreateView(generics.CreateAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]



class VisitListView(generics.ListAPIView):
    queryset = Visit.objects.all().order_by('-created_at')  
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]


class VisitDetailView(generics.RetrieveAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 


class VisitUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
