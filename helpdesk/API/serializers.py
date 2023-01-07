from rest_framework import serializers

from helpdesk.models import Ticket, Comment, CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2', 'token']
        extra_kwargs = {
            'token': {
                'source': 'auth_token',
                'read_only': True,
            },
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('The two password fields dont match')
        return data

    def create(self, validated_data):
        user = CustomUser(username=validated_data['username'],
                          email=validated_data['email'],
                          first_name=validated_data['first_name'],
                          last_name=validated_data['last_name'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname']
        extra_kwargs = {
            'name': {
                'source': 'first_name',
            },
            'surname': {
                'source': 'last_name',
            },
        }


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['comment', 'author', 'ticket', 'created']
        extra_kwargs = {
            'comment': {
                'source': 'body',
            },
            'ticket': {
                'write_only': True,
            },
            'created': {
                'format': '%Y-%m-%d %H:%M',
            },
        }

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        ticket = data.get('ticket')

        if ticket.status != Ticket.ACTIVE_STATUS:
            raise serializers.ValidationError({
                'ticket': 'You cannot comment on an ticket that is not in the active status'
            })

        if user != ticket.user and not user.is_staff:
            raise serializers.ValidationError({
                'ticket': 'Only the author or administrator can leave a comment on the ticket'
            })

        return data


class TicketGetOrCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'priority', 'status', 'author', 'created', 'comments']
        extra_kwargs = {
            'created': {
                'format': '%Y-%m-%d %H:%M',
            },
            'priority': {
                'required': True,
            },
            'status': {
                'read_only': True,
            },
        }


class TicketUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['description', 'priority']

    def validate(self, data):
        pass
# active status only


class ChangeTicketStatusSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True)

    class Meta:
        model = Ticket
        fields = ['status', 'comment']

    def validate(self, data):
        pass
