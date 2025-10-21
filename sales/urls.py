from django.urls import path
from .views import CreateSalesFromVisit,SalesListView, SalesDetailView, AdminSalesListView

urlpatterns = [
    path('create-from-visit/<int:visit_id>/', CreateSalesFromVisit.as_view(), name='sales-create-from-visit'),
    path("sales-list/", SalesListView.as_view(), name="sales-list"),
    path("admin-sales-list/", AdminSalesListView.as_view(), name="admin-sales-list"),
    path("sales-details/<int:id>/", SalesDetailView.as_view(), name="sales-detail"),
     path("admin-sales-details/<int:id>/", SalesDetailView.as_view(), name="admin-sales-detail"),
]
