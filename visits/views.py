from rest_framework import generics, permissions
from .models import Visit
from .serializers import VisitUpdateSerializer, VisitSerializer

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Visit
from .serializers import VisitSerializer

class VisitCreateView(generics.CreateAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)        # 🔍 Check what React sends
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data)
        else:
            print("Errors:", serializer.errors)   # 🔍 See why 400
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VisitListView(generics.ListAPIView):
    queryset = Visit.objects.all().order_by('-created_at')  
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]


class VisitDetailView(generics.RetrieveAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Visit
from .serializers import VisitUpdateSerializer

class VisitUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
       
        instance = self.get_object()
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
