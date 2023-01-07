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
    serializer_class = TicketGetOrCreateSerializer
    update_serializer_class = TicketUpdateSerializer
    http_method_names = ['get', 'post', 'patch']
    # permission_classes = []    ****post and patch only client

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return self.update_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RestoreTicketViewSet(viewsets.ModelViewSet):
    pass


class ChangeTicketStatusViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = ChangeTicketStatusSerializer
    http_method_names = ['patch']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
