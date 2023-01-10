from django.db import transaction
from rest_framework import viewsets, permissions

from helpdesk.API.permissions import IsUserOrAdminReadOnly
from helpdesk.API.serializers import RegistrationSerializer, TicketUpdateSerializer, CommentSerializer,\
    TicketGetOrCreateSerializer, ChangeTicketStatusSerializer
from helpdesk.models import CustomUser, Ticket, Comment


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.exclude(status=Ticket.RESTORED_STATUS)
    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsUserOrAdminReadOnly]

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return TicketUpdateSerializer
        return TicketGetOrCreateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RestoreTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.filter(status=Ticket.RESTORED_STATUS)
    serializer_class = TicketGetOrCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class ChangeTicketStatusViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.exclude(status=Ticket.COMPLETED_STATUS)
    serializer_class = ChangeTicketStatusSerializer
    http_method_names = ['patch']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def perform_update(self, serializer):
        ticket = serializer.instance
        current_status = ticket.status
        changed_status = serializer.validated_data.get('status')
        comment = serializer.validated_data.get('comment')
        user = self.request.user

        if changed_status == Ticket.RESTORED_STATUS and comment:
            with transaction.atomic():
                Comment.objects.create(author=user,
                                       ticket=ticket,
                                       topic=Comment.RESTORE_TOPIC,
                                       body=comment)
                serializer.save()

        elif changed_status == Ticket.REJECTED_STATUS and current_status == Ticket.ACTIVE_STATUS:
            with transaction.atomic():
                Comment.objects.create(author=user,
                                       ticket=ticket,
                                       topic=Comment.REJECT_TOPIC,
                                       body=comment)
                serializer.save()

        elif changed_status == Ticket.REJECTED_STATUS and current_status == Ticket.RESTORED_STATUS:
            ticket.delete()

        else:
            return super().perform_update(serializer)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
