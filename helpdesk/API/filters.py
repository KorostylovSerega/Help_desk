from django.db.models import Q
from rest_framework import filters, serializers


class StatusPriorityFilter(filters.BaseFilterBackend):
    statuses = {
        'active': '1',
        'processed': '2',
        'rejected': '3',
        'restored': '4',
        'completed': '5',
    }
    priorities = {
        'high': '1',
        'medium': '2',
        'low': '3',
    }

    def filter_queryset(self, request, queryset, view):
        status_query = request.query_params.get('status')
        priority_query = request.query_params.get('priority')

        if status_query or priority_query:
            status = self.statuses.get(status_query.lower()) if status_query else self.statuses.values()
            if status is None:
                raise serializers.ValidationError({
                    'status': f'Select a valid choice. {status_query} is not one of the available choices.'
                })
            priority = self.priorities.get(priority_query.lower()) if priority_query else self.priorities.values()
            if priority is None:
                raise serializers.ValidationError({
                    'status': f'Select a valid choice. {priority_query} is not one of the available choices.'
                })
            queryset = queryset.filter(Q(status__in=status) & Q(priority__in=priority))
        return queryset
