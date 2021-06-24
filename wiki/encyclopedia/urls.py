from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:TITLE>", views.entry, name="entry"),
    path("create/", views.create, name="create"),
    path("edit/", views.edit, name="edit"),
    path("random/", views.random, name="random")
]
