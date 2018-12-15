from django.contrib import admin
from django.urls import path

from . import views

app_name = 'Interface'
urlpatterns = [
    path('show/', views.show)
]

