from django.contrib.auth import views
from django.urls import path

from helpdesk.views import UserCreateView, TicketCreateView, TicketListView

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('', TicketListView.as_view(), name='home'),
    path('add-ticket/', TicketCreateView.as_view(), name='add_ticket')
]
