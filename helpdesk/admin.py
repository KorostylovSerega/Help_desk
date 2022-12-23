from django.contrib import admin

from helpdesk.models import CustomUser, Ticket

admin.site.register(CustomUser)
admin.site.register(Ticket)
