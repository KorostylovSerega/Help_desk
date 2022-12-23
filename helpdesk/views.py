from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from helpdesk.forms import UserCreateForm, TicketCreateForm
from helpdesk.models import Ticket


class UserCreateView(CreateView):
    form_class = UserCreateForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        valid = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return valid


class TicketCreateView(LoginRequiredMixin, CreateView):
    form_class = TicketCreateForm
    template_name = 'helpdesk/create_ticket.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        ticket = form.save(commit=False)
        user = self.request.user
        ticket.user = user
        ticket.save()
        return super().form_valid(form)
