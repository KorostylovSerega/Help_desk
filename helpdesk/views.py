from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from helpdesk.forms import UserCreateForm, CommentCreateForm
from helpdesk.models import CustomUser, Ticket


class UserCreateView(CreateView):
    form_class = UserCreateForm
    model = CustomUser
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
    login_url = reverse_lazy('login')
    model = Ticket
    fields = ['title', 'description', 'priority']
    template_name = 'helpdesk/ticket_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        ticket = form.save(commit=False)
        user = self.request.user
        ticket.user = user
        ticket.save()
        return super().form_valid(form)


class TicketListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Ticket
    template_name = 'helpdesk/home.html'
    queryset = Ticket.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_superuser:
            return queryset.filter(user=user)
        return queryset


class TicketDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('login')
    model = Ticket
    template_name = 'helpdesk/ticket_detail.html'
    extra_context = {'form': CommentCreateForm}


class CommentCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = CommentCreateForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        ticket_id = self.kwargs.get('pk')
        ticket = Ticket.objects.get(id=ticket_id)
        author = self.request.user
        comment.ticket = ticket
        comment.author = author
        comment.save()
        return super().form_valid(form)
