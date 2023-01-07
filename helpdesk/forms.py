from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import HiddenInput

from helpdesk.models import CustomUser, Ticket, Comment


class UserCreateForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
        }


class CommentCreateForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['body']

    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        current_status = self.ticket.status
        ticket_author = self.ticket.user
        comment_author = self.request.user

        if current_status != Ticket.ACTIVE_STATUS:
            self.add_error(None, 'You cannot comment on an ticket that is not in the active status.')

        if ticket_author != comment_author and not comment_author.is_staff:
            self.add_error(None, 'Only the author or administrator can leave a comment on the ticket.')


class TicketUpdateForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['description', 'priority']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        current_status = self.instance.status
        author = self.instance.user
        user = self.request.user

        if current_status != Ticket.ACTIVE_STATUS:
            self.add_error(None, 'You cannot edit an ticket if it is not in the Active status.')

        if author != user:
            self.add_error(None, 'You can change only your ticket.')


class ChangeTicketStatusForm(forms.ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        changed_status = cleaned_data.get('status')
        current_status = self.instance.status
        author = self.instance.user
        user = self.request.user
        user_is_admin = user.is_staff

        if changed_status == current_status:
            self.add_error('status', 'Status should be different.')

        if user != author and not user_is_admin:
            self.add_error('status', 'You can change status only your ticket.')

        if changed_status == Ticket.ACTIVE_STATUS:
            self.add_error('status', 'Status ACTIVE cannot be set by user.')

        if changed_status in [Ticket.PROCESSED_STATUS, Ticket.REJECTED_STATUS] and \
                current_status not in [Ticket.ACTIVE_STATUS, Ticket.RESTORED_STATUS] and \
                not user_is_admin:
            self.add_error('status', 'Status can only be set if the ticket is active or restored.')

        if changed_status == Ticket.RESTORED_STATUS and \
                current_status != Ticket.REJECTED_STATUS and user_is_admin:
            self.add_error('status', 'You can only restore an ticket if it was rejected.')

        if changed_status == Ticket.COMPLETED_STATUS and \
                current_status != Ticket.PROCESSED_STATUS and not user_is_admin:
            self.add_error('status', 'You can complete the ticket only if it in the status PROCESSED.')
