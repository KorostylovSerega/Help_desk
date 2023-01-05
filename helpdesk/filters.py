import django_filters

from helpdesk.models import Ticket


class TicketFilter(django_filters.FilterSet):

    class Meta:
        model = Ticket
        fields = ['priority', 'status']
