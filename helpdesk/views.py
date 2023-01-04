from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib import messages

from helpdesk.filters import TicketFilter
from helpdesk.forms import UserCreateForm, ChangeTicketStatusForm, CommentCreateForm, TicketUpdateForm
from helpdesk.models import Ticket, Comment


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


class TicketCreateView(UserPassesTestMixin, CreateView):
    model = Ticket
    fields = ['title', 'description', 'priority']
    template_name = 'helpdesk/ticket_create.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and not user.is_staff

    def form_valid(self, form):
        ticket = form.save(commit=False)
        user = self.request.user
        ticket.user = user
        ticket.save()
        return super().form_valid(form)


class TicketUpdateView(UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = TicketUpdateForm
    template_name = 'helpdesk/ticket_update.html'

    def test_func(self):
        ticket = self.get_object()
        user = self.request.user
        return ticket.user == user and ticket.status == Ticket.ACTIVE_STATUS

    def get_success_url(self):
        return reverse_lazy('detail_ticket', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        error_list = form.errors.get('__all__')
        for error in error_list:
            messages.error(self.request, error)
        return HttpResponseRedirect(reverse_lazy('home'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class TicketListView(LoginRequiredMixin, ListView):
    queryset = Ticket.objects.exclude(status=Ticket.RESTORED_STATUS)
    template_name = 'helpdesk/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = TicketFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset.exclude(status=Ticket.REJECTED_STATUS)


class RestoreTicketListView(UserPassesTestMixin, ListView):
    queryset = Ticket.objects.filter(status=Ticket.RESTORED_STATUS)
    template_name = 'helpdesk/ticket_restore.html'

    def test_func(self):
        return self.request.user.is_staff


class TicketDetailView(UserPassesTestMixin, DetailView):
    model = Ticket
    template_name = 'helpdesk/ticket_detail.html'
    comment_form = CommentCreateForm
    accept_form = ChangeTicketStatusForm(initial={'status': Ticket.PROCESSED_STATUS})
    reject_form = ChangeTicketStatusForm(initial={'status': Ticket.REJECTED_STATUS})
    complete_form = ChangeTicketStatusForm(initial={'status': Ticket.COMPLETED_STATUS})
    restore_form = ChangeTicketStatusForm(initial={'status': Ticket.RESTORED_STATUS})

    def test_func(self):
        ticket = self.get_object()
        user = self.request.user
        return ticket.user == user or user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_status = self.object.status
        user_is_admin = self.request.user.is_staff

        if ticket_status == Ticket.ACTIVE_STATUS:
            context['comment_form'] = self.comment_form

        if ticket_status in [Ticket.ACTIVE_STATUS, Ticket.RESTORED_STATUS] and user_is_admin:
            self.accept_form.fields['comment'].widget = forms.HiddenInput()
            context['accept_form'] = self.accept_form

            if ticket_status == Ticket.ACTIVE_STATUS:
                self.reject_form.fields['comment'].required = True
                self.reject_form.fields['comment'].widget = forms.Textarea()
                context['reject_form'] = self.reject_form

            elif ticket_status == Ticket.RESTORED_STATUS:
                self.reject_form.fields['comment'].required = False
                self.reject_form.fields['comment'].widget = forms.HiddenInput()
                context['reject_form'] = self.reject_form

        if ticket_status == Ticket.PROCESSED_STATUS and user_is_admin:
            self.complete_form.fields['comment'].widget = forms.HiddenInput()
            context['complete_form'] = self.complete_form

        if ticket_status == Ticket.REJECTED_STATUS and not user_is_admin:
            context['restore_form'] = self.restore_form
        return context


class ChangeTicketStatusView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = ChangeTicketStatusForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        ticket = Ticket.objects.get(id=self.object.pk)
        current_status = ticket.status
        changed_status = form.cleaned_data.get('status')
        comment = form.cleaned_data.get('comment')
        if changed_status in [Ticket.PROCESSED_STATUS, Ticket.COMPLETED_STATUS]:
            return super().form_valid(form)
        if changed_status == Ticket.RESTORED_STATUS:
            if not comment:
                return super().form_valid(form)

            with transaction.atomic():
                self.object.save()
                Comment.objects.create(author=self.request.user,
                                       ticket=self.object,
                                       topic=Comment.RESTORE_TOPIC,
                                       body=comment)
            return HttpResponseRedirect(self.success_url)

        if changed_status == Ticket.REJECTED_STATUS:
            if current_status == Ticket.ACTIVE_STATUS:

                with transaction.atomic():
                    form.save()
                    Comment.objects.create(author=self.request.user,
                                           ticket=self.object,
                                           topic=Comment.REJECT_TOPIC,
                                           body=comment)
                return HttpResponseRedirect(self.success_url)

        self.object.delete()
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        error_list = form.errors.get('status')
        for error in error_list:
            messages.error(self.request, error)
        return HttpResponseRedirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentCreateForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.ticket = form.ticket
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        error_list = form.errors.get('__all__')
        for error in error_list:
            messages.error(self.request, error)
        return HttpResponseRedirect(reverse_lazy('home'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        ticket_id = self.kwargs.get('pk')
        ticket = Ticket.objects.get(id=ticket_id)
        kwargs['ticket'] = ticket
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('detail_ticket', kwargs={'pk': self.object.ticket_id})
