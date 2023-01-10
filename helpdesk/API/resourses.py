from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from helpdesk.API.permissions import IsUserOrAdminReadOnly
from helpdesk.API.serializers import RegistrationSerializer, TicketUpdateSerializer, CommentSerializer,\
    TicketGetOrCreateSerializer, ChangeTicketStatusSerializer
from helpdesk.models import CustomUser, Ticket, Comment


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]


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

    @action(detail=True,
            methods=['patch'],
            queryset=Ticket.objects.exclude(status=Ticket.COMPLETED_STATUS),
            permission_classes=[IsAuthenticated])
    def change_ticket_status(self, request, pk=None):
        ticket = self.get_object()
        context = self.get_serializer_context()
        serializer = ChangeTicketStatusSerializer(ticket, data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        current_status = ticket.status
        changed_status = serializer.validated_data.get('status')
        comment = serializer.validated_data.get('comment')

        if (changed_status == Ticket.RESTORED_STATUS and comment) or \
                (changed_status == Ticket.REJECTED_STATUS and
                 current_status == Ticket.ACTIVE_STATUS):

            new_comment = Comment(author=request.user,
                                  ticket=ticket,
                                  body=comment)

            if changed_status == Ticket.RESTORED_STATUS:
                new_comment.topic = Comment.RESTORE_TOPIC
            else:
                new_comment.topic = Comment.REJECT_TOPIC

            with transaction.atomic():
                new_comment.save()
                serializer.save()

            return Response(serializer.data)

        if changed_status == Ticket.REJECTED_STATUS and \
                current_status == Ticket.RESTORED_STATUS:
            ticket.delete()
            return Response({'detail': 'Ticket deleted.'})

        serializer.save()
        return Response(serializer.data)


class RestoreTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.filter(status=Ticket.RESTORED_STATUS)
    serializer_class = TicketGetOrCreateSerializer
    permission_classes = [IsAdminUser]


# class ChangeTicketStatusViewSet(viewsets.ModelViewSet):
#     queryset = Ticket.objects.exclude(status=Ticket.COMPLETED_STATUS)
#     serializer_class = ChangeTicketStatusSerializer
#     http_method_names = ['patch']
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         user = self.request.user
#         if not user.is_staff:
#             return queryset.filter(user=user)
#         return queryset
#
#     def perform_update(self, serializer):
#         ticket = serializer.instance
#         current_status = ticket.status
#         changed_status = serializer.validated_data.get('status')
#         comment = serializer.validated_data.get('comment')
#         user = self.request.user
#
#         if changed_status == Ticket.RESTORED_STATUS and comment:
#             with transaction.atomic():
#                 Comment.objects.create(author=user,
#                                        ticket=ticket,
#                                        topic=Comment.RESTORE_TOPIC,
#                                        body=comment)
#                 serializer.save()
#
#         elif changed_status == Ticket.REJECTED_STATUS and current_status == Ticket.ACTIVE_STATUS:
#             with transaction.atomic():
#                 Comment.objects.create(author=user,
#                                        ticket=ticket,
#                                        topic=Comment.REJECT_TOPIC,
#                                        body=comment)
#                 serializer.save()
#
#         elif changed_status == Ticket.REJECTED_STATUS and current_status == Ticket.RESTORED_STATUS:
#             ticket.delete()
#
#         else:
#             serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
