from rest_framework import viewsets

from helpdesk.API.serializers import TicketSerializer, CommentSerializer
from helpdesk.models import Ticket, Comment


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
