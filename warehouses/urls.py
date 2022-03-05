from django.urls import path
from . import views


app_name = 'warehouses'

urlpatterns = [
    path('workflow/<int:product_id>/', views.product_workflow, name="product_workflow")

]
