from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin

from config.settings import INACTIVITY_TIME_LIMIT


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            now = datetime.now()
            last_activity_time = request.session.get('last_activity_time', now.isoformat())
            inactivity_period = now - datetime.fromisoformat(last_activity_time)
            if inactivity_period.seconds > INACTIVITY_TIME_LIMIT:
                logout(request)
                return HttpResponseRedirect(reverse_lazy('login'))
            request.session['last_activity_time'] = now.isoformat()


class CounterUserAction(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_staff and request.method == 'GET':
            counter_action = request.session.get('counter_action', 0)
            counter_action += 1
            request.session['counter_action'] = counter_action
            messages.info(request, f'{counter_action}')
