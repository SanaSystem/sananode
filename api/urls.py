from django.urls import path
from .views import UserListView, UserDetailView, MedBlockListView, MedBlockDetailView, api_root

urlpatterns = [
    path('', api_root),
    path('user/', UserListView.as_view(), name="user-list"),
    path('user/<str:username>', UserDetailView.as_view(), name="user-detail"),
    path('medblock/', MedBlockListView.as_view(), name="medblock-list"),
    path('medblock/<int:pk>', MedBlockDetailView.as_view(), name="medblock-detail"),
]