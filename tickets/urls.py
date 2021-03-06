from django.urls import path

from . import views


app_name = 'tickets'


urlpatterns = [
    path('', views.tickets_list, name="tickets_list"),
    path('filter/<str:filter>', views.tickets_list, name="tickets_list_filter"),
    path('details/<int:ticket_id>/', views.ticket_details, name="ticket_details"),
    path('create/', views.create_ticket, name="create_ticket"),
]
