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
        author = self.instance.user
        changed_status = cleaned_data.get('status')
        current_status = self.instance.status
        if self.instance.status != changed_status:
            self.add_error('status', 'test error')
        return cleaned_data
