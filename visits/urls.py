from django.urls import path
from .views import VisitCreateView, VisitListView,VisitDetailView, VisitUpdateView, AdminVisitListView, AdminVisitDetailView

urlpatterns = [
    path('visit-create/', VisitCreateView.as_view(), name='create-visit'),
    path('visit-list/', VisitListView.as_view(), name='list-visits'),
    path('admin-visit-list/', AdminVisitListView.as_view(), name='admin-list-visits'),
    path('visit-details/<int:id>/', VisitDetailView.as_view(), name='detail-visit'),
    path('admin-visit-details/<int:id>/',AdminVisitDetailView.as_view(), name='admin-detail-visit'),
    path('visit-update/<int:id>/update/', VisitUpdateView.as_view(), name='update-visit'),
    
 
]
