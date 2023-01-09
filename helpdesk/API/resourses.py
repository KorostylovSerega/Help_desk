from django.db import transaction
from rest_framework import viewsets

from helpdesk.API.serializers import RegistrationSerializer, TicketUpdateSerializer, CommentSerializer, \
    TicketGetOrCreateSerializer, ChangeTicketStatusSerializer
from helpdesk.models import CustomUser, Ticket, Comment


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['post']


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.exclude(status=Ticket.RESTORED_STATUS)
    http_method_names = ['get', 'post', 'patch']
    # permission_classes = []    ****post and patch only client

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


class RestoreTicketViewSet(viewsets.ModelViewSet):
    # permission_classes = []    ****only staff
    pass


class ChangeTicketStatusViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = ChangeTicketStatusSerializer
    http_method_names = ['patch']
    # permission_classes = []    ****post and patch only client

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

        if changed_status in [Ticket.PROCESSED_STATUS, Ticket.COMPLETED_STATUS]:
            serializer.save()

        elif changed_status == Ticket.RESTORED_STATUS:
            if comment is not None:
                with transaction.atomic():
                    Comment.objects.create(author=user,
                                           ticket=ticket,
                                           topic=Comment.RESTORE_TOPIC,
                                           body=comment)
                    serializer.save()
            else:
                serializer.save()

        elif changed_status == Ticket.REJECTED_STATUS:
            if current_status == Ticket.ACTIVE_STATUS:
                with transaction.atomic():
                    Comment.objects.create(author=user,
                                           ticket=ticket,
                                           topic=Comment.REJECT_TOPIC,
                                           body=comment)
                    serializer.save()



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['post']
    # permission_classes = []    ****authenticate

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
