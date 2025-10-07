from django.urls import path
from . import views

urlpatterns = [
    path('list-sales/', views.sales_list, name='sales_list'),
    path('salepayment-detail/<int:sale_id>/', views.sales_detail, name='sales_detail'),  # optional, for detail view
]
