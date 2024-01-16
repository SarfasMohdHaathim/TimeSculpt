from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('watch/<str:watch_name>/<int:watch_id>/', WatchDetailView.as_view(), name='watch_detail'),
]