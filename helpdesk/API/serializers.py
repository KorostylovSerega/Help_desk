from rest_framework import serializers

from helpdesk.models import Ticket, Comment, CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    comment_author = UserSerializer(source='author', required=False)

    class Meta:
        model = Comment
        fields = ['comment_author', 'author', 'ticket', 'topic', 'body', 'created']
        extra_kwargs = {
            'author': {'write_only': True},
            'ticket': {'write_only': True},
        }


class TicketSerializer(serializers.ModelSerializer):
    ticket_author = UserSerializer(source='user', required=False)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Ticket
        fields = ['user', 'ticket_author', 'title', 'description', 'priority', 'status', 'created', 'comments']
        extra_kwargs = {
            'user': {'write_only': True},
        }
