from django.contrib.auth import views
from django.urls import path

from helpdesk.views import UserCreateView, TicketCreateView, TicketUpdateView,\
    TicketListView, TicketDetailView, CommentCreateView, ChangeTicketStatusView,\
    RestoreTicketListView

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('', TicketListView.as_view(), name='home'),
    # path('reject-ticket', RejectTicketListView.as_view(), name='reject_ticket'),
    path('restore-ticket', RestoreTicketListView.as_view(), name='restore_ticket'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='detail_ticket'),
    path('add-ticket/', TicketCreateView.as_view(), name='add_ticket'),
    path('update-ticket/<int:pk>/', TicketUpdateView.as_view(), name='update_ticket'),
    path('update-ticket-status/<int:pk>/', ChangeTicketStatusView.as_view(), name='change_status'),
    path('add-comment/<int:pk>', CommentCreateView.as_view(), name='add_comment'),
]
