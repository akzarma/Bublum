from django.contrib import admin
from django.urls import path

from . import views

app_name = 'Interface'
urlpatterns = [
    path('show/', views.show),
    path('prediction/', views.vehicle_model, name='prediction'),
    path('get_frames/', views.get_frames, name='get_frames')
]
