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
            raise serializers.ValidationError('The two password fields dont match.')
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
        }

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        ticket = data.get('ticket')

        if ticket.status != Ticket.ACTIVE_STATUS:
            raise serializers.ValidationError({
                'ticket': 'You cannot comment on an ticket that is not in the active status.'
            })

        if user != ticket.user and not user.is_staff:
            raise serializers.ValidationError({
                'ticket': 'Only the author or administrator can leave a comment on the ticket.'
            })

        return data


class TicketGetOrCreateSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    author = UserSerializer(source='user', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'priority_id', 'priority', 'status', 'author', 'created', 'comments']
        extra_kwargs = {
            'priority_id': {
                'source': 'priority',
                'write_only': True,
                'required': True,
            },
        }


class TicketUpdateSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'priority_id', 'priority', 'status']
        extra_kwargs = {
            'title': {
                'read_only': True,
            },
            'priority_id': {
                'source': 'priority',
                'write_only': True,
            },
        }

    def validate(self, data):
        if self.instance.status != Ticket.ACTIVE_STATUS:
            raise serializers.ValidationError('You cannot edit an ticket if it is not in the Active status.')
        return data


class ChangeTicketStatusSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    comment = serializers.CharField(write_only=True)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'status_id', 'status', 'comment']
        read_only_fields = ['title', 'description']
        extra_kwargs = {
            'status_id': {
                'source': 'status',
                'write_only': True,
            },
        }

    def validate(self, data):
        comment = data.get('comment')
        changed_status = data.get('status')
        current_status = self.instance.status
        request = self.context.get('request')
        user_is_admin = request.user.is_staff

        if changed_status is None:
            raise serializers.ValidationError({
                'status_id': 'This field is required.'
            })

        if changed_status == current_status:
            raise serializers.ValidationError({
                'status_id': 'Status should be different.'
            })

        if changed_status == Ticket.ACTIVE_STATUS:
            raise serializers.ValidationError({
                'status_id': 'Status ACTIVE cannot be set by user.'
            })

        if changed_status in [Ticket.PROCESSED_STATUS, Ticket.REJECTED_STATUS]:
            if not user_is_admin:
                raise serializers.ValidationError('Status can only be changed by the administrator.')
            if current_status not in [Ticket.ACTIVE_STATUS, Ticket.RESTORED_STATUS]:
                raise serializers.ValidationError({
                    'status_id': 'Status can only be changed if the ticket is active or restored.'
                })
            if changed_status == Ticket.REJECTED_STATUS and \
                    current_status == Ticket.ACTIVE_STATUS and comment is None:
                raise serializers.ValidationError({
                    'comment': 'This field is required.'
                })

        if changed_status == Ticket.RESTORED_STATUS:
            if user_is_admin:
                raise serializers.ValidationError('Administrator cant restore tickets.')
            if current_status != Ticket.REJECTED_STATUS:
                raise serializers.ValidationError({
                    'status_id': 'You can only restore an ticket if it was rejected.'
                })

        if changed_status == Ticket.COMPLETED_STATUS:
            if not user_is_admin:
                raise serializers.ValidationError('Status can only be changed by the administrator.')
            if current_status != Ticket.PROCESSED_STATUS:
                raise serializers.ValidationError({
                    'status_id': 'You can complete the ticket only if it in the status PROCESSED.'
                })

        return data
