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



class UserVerificationDetailView(generics.RetrieveAPIView):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id'

    def get_queryset(self):
        user = self.request.user
        return Verification.objects.filter(submitted_by=user, content_type__model='visit')


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Verification, VerificationMessage
from .serializers import VerificationMessageSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Verification, VerificationMessage

class VerificationMessageListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, verification_id):
        try:
            verification = Verification.objects.get(id=verification_id)
        except Verification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        all_messages = []

        
        if verification.submitted_by:
            sender = verification.submitted_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"user-{verification.id}",
                "sender_name": sender_name,
                "message": verification.user_message or "(no message provided)",
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
            })

       
        chat_messages = VerificationMessage.objects.filter(verification=verification).order_by("created_at")
        for msg in chat_messages:
            sender = msg.sender
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": msg.id,
                "sender_name": sender_name,
                "message": msg.message or "(no message provided)",
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            })

        
        if verification.supervisor_message and verification.verified_by:
            sender = verification.verified_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"supervisor-{verification.id}",
                "sender_name": sender_name,
                "message": verification.supervisor_message or "(no message provided)",
                "created_at": verification.verified_at.isoformat() if verification.verified_at else None,
            })

        
        all_messages.sort(key=lambda m: m["created_at"] or "")

        return Response(all_messages)



class VerificationMessageCreateView(generics.CreateAPIView):
    serializer_class = VerificationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        verification_id = kwargs['verification_id']
        try:
            verification = Verification.objects.get(id=verification_id)
        except Verification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        message_text = request.data.get('message')
        if not message_text:
            return Response({"message": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        message = VerificationMessage.objects.create(
            verification=verification,
            sender=request.user,
            message=message_text
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)







class UserVerificationMessageListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, verification_id):
        try:
            verification = Verification.objects.get(id=verification_id)
        except Verification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        all_messages = []

       
        if verification.submitted_by:
            sender = verification.submitted_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"user-{verification.id}",
                "sender_name": sender_name,
                "message": verification.user_message or "(no message provided)",
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
            })

    
        chat_messages = VerificationMessage.objects.filter(verification=verification).order_by("created_at")
        for msg in chat_messages:
            sender = msg.sender
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": msg.id,
                "sender_name": sender_name,
                "message": msg.message or "(no message provided)",
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            })

        
        if verification.supervisor_message and verification.verified_by:
            sender = verification.verified_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"supervisor-{verification.id}",
                "sender_name": sender_name,
                "message": verification.supervisor_message or "(no message provided)",
                "created_at": verification.verified_at.isoformat() if verification.verified_at else None,
            })

       
        all_messages.sort(key=lambda m: m["created_at"] or "")

        return Response(all_messages)



class UserVerificationMessageCreateView(generics.CreateAPIView):
    serializer_class = VerificationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        verification_id = kwargs['verification_id']
        try:
            verification = Verification.objects.get(id=verification_id)
        except Verification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        message_text = request.data.get('message')
        if not message_text:
            return Response({"message": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        message = VerificationMessage.objects.create(
            verification=verification,
            sender=request.user,
            message=message_text
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
