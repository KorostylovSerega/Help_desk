from django.contrib.auth import views
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as rest_views

from helpdesk.API.resourses import RegistrationViewSet, TicketViewSet, CommentViewSet,\
    RestoreTicketViewSet
from helpdesk.views import UserCreateView, TicketCreateView, TicketUpdateView,\
    TicketListView, TicketDetailView, CommentCreateView, ChangeTicketStatusView,\
    RestoreTicketListView


router = routers.SimpleRouter()
router.register(r'registration', RegistrationViewSet)
router.register(r'ticket', TicketViewSet)
router.register(r'restore-ticket', RestoreTicketViewSet)
# router.register(r'change-ticket-status', ChangeTicketStatusViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('', TicketListView.as_view(), name='home'),
    path('restore-ticket', RestoreTicketListView.as_view(), name='restore_ticket'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='detail_ticket'),
    path('add-ticket/', TicketCreateView.as_view(), name='add_ticket'),
    path('update-ticket/<int:pk>/', TicketUpdateView.as_view(), name='update_ticket'),
    path('update-ticket-status/<int:pk>/', ChangeTicketStatusView.as_view(), name='change_status'),
    path('add-comment/<int:pk>', CommentCreateView.as_view(), name='add_comment'),

    path('api/', include(router.urls)),
    path('api/get-auth-token/', rest_views.obtain_auth_token)
]
