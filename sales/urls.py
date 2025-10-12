from django.urls import path
from .views import CreateSalesFromVisit,SalesListView, SalesDetailView 

urlpatterns = [
    # URL to create a sales order from a visit
    path('create-from-visit/<int:visit_id>/', CreateSalesFromVisit.as_view(), name='sales-create-from-visit'),
    path("sales-list/", SalesListView.as_view(), name="sales-list"),
    path("sales-details/<int:id>/", SalesDetailView.as_view(), name="sales-detail"),
]
