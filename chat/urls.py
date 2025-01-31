from django.urls import path

from . import views

urlpatterns = [
    path("async/", views.chat_async, name="index_async"),
    path("sync/", views.chat_sync, name="index_sync"),
]