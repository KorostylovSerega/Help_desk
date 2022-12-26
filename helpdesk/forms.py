from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import Textarea, HiddenInput

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


class ChangeStatusForm(forms.ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': HiddenInput(),
        }
