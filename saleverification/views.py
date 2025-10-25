from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import SalesVerification, SalesVerificationMessage
from .serializers import SalesVerificationSerializer, SupervisorUpdateSalesVerificationSerializer, SalesVerificationMessageSerializer


# ---------------- Submit Sales Verification ----------------
class SubmitSalesVerificationView(generics.CreateAPIView):
    queryset = SalesVerification.objects.all()
    serializer_class = SalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


# ---------------- List Submitted Sales Verifications ----------------
class UserSubmittedSalesVerificationsView(generics.ListAPIView):
    serializer_class = SalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SalesVerification.objects.filter(submitted_by=user).order_by('-created_at')


# ---------------- Supervisor Sales Verifications ----------------
class SupervisorSalesVerificationsView(generics.ListAPIView):
    serializer_class = SalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SalesVerification.objects.filter(sent_to=user)


class SupervisorSalesVerificationDetailView(generics.RetrieveAPIView):
    serializer_class = SalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id'

    def get_queryset(self):
        user = self.request.user
        return SalesVerification.objects.filter(sent_to=user)


class SupervisorUpdateSalesVerificationView(generics.UpdateAPIView):
    serializer_class = SupervisorUpdateSalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id'

    def get_queryset(self):
        user = self.request.user
        return SalesVerification.objects.filter(sent_to=user)


class UserSalesVerificationDetailView(generics.RetrieveAPIView):
    serializer_class = SalesVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'verification_id'

    def get_queryset(self):
        user = self.request.user
        return SalesVerification.objects.filter(submitted_by=user)


# ---------------- Sales Verification Messages ----------------
class SalesVerificationMessageListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, verification_id):
        try:
            verification = SalesVerification.objects.get(id=verification_id)
        except SalesVerification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        all_messages = []

        # User message
        if verification.submitted_by:
            sender = verification.submitted_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"user-{verification.id}",
                "sender_name": sender_name,
                "message": verification.user_message or "(no message provided)",
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
            })

        # Chat messages
        chat_messages = SalesVerificationMessage.objects.filter(verification=verification).order_by("created_at")
        for msg in chat_messages:
            sender = msg.sender
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": msg.id,
                "sender_name": sender_name,
                "message": msg.message or "(no message provided)",
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            })

        # Supervisor message
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


class SalesVerificationMessageCreateView(generics.CreateAPIView):
    serializer_class = SalesVerificationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        verification_id = kwargs['verification_id']
        try:
            verification = SalesVerification.objects.get(id=verification_id)
        except SalesVerification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        message_text = request.data.get('message')
        if not message_text:
            return Response({"message": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        message = SalesVerificationMessage.objects.create(
            verification=verification,
            sender=request.user,
            message=message_text
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)





# ---------------- Sales Verification Messages ----------------
class UserSalesVerificationMessageListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, verification_id):
        try:
            verification = SalesVerification.objects.get(id=verification_id)
        except SalesVerification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        all_messages = []

        # User message
        if verification.submitted_by:
            sender = verification.submitted_by
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": f"user-{verification.id}",
                "sender_name": sender_name,
                "message": verification.user_message or "(no message provided)",
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
            })

        # Chat messages
        chat_messages = SalesVerificationMessage.objects.filter(verification=verification).order_by("created_at")
        for msg in chat_messages:
            sender = msg.sender
            sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email
            all_messages.append({
                "id": msg.id,
                "sender_name": sender_name,
                "message": msg.message or "(no message provided)",
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            })

        # Supervisor message
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


class UserSalesVerificationMessageCreateView(generics.CreateAPIView):
    serializer_class = SalesVerificationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        verification_id = kwargs['verification_id']
        try:
            verification = SalesVerification.objects.get(id=verification_id)
        except SalesVerification.DoesNotExist:
            return Response({"detail": "Verification not found"}, status=status.HTTP_404_NOT_FOUND)

        message_text = request.data.get('message')
        if not message_text:
            return Response({"message": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        message = SalesVerificationMessage.objects.create(
            verification=verification,
            sender=request.user,
            message=message_text
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

