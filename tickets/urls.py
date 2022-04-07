from django.urls import path

from . import views


app_name = 'tickets'


urlpatterns = [
    path('', views.tickets_list, name="tickets_list"),
    path('details/<int:ticket_id>/', views.ticket_details, name="ticket_details"),

]
