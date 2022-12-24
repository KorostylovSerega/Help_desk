from django.contrib import admin

from helpdesk.models import CustomUser, Ticket, Comment

admin.site.register(CustomUser)
admin.site.register(Ticket)
admin.site.register(Comment)
