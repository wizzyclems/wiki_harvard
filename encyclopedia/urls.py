from django.urls import path

from . import views

#app_name = 'wiki'

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("create", views.create, name="create"),
    path("wiki", views.index, name="index"),
    path("search", views.search, name="search"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("random-page", views.randomPage, name="random_page")
]
