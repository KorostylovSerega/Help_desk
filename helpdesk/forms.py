from django.contrib.auth.forms import UserCreationForm
from django import forms

from helpdesk.models import CustomUser, Ticket


class UserCreateForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
        }


# class TicketCreateForm(forms.ModelForm):
#
#     class Meta:
#         model = Ticket
#         fields = ['title', 'description', 'priority']
