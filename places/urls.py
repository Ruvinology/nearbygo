from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "places"

urlpatterns = [
    path("", views.place_list, name="list"),
    path("places/", RedirectView.as_view(pattern_name="places:list", query_string=True, permanent=False)),
    path("places/<slug:slug>/", views.place_detail, name="detail"),
    path("map/", views.map_view, name="map"),
    path("about/", views.about, name="about"),
]
