from django.urls import path

from . import views

app_name = "planner"

urlpatterns = [
    path("", views.plan_view, name="plan"),
    path("add/", views.plan_add, name="add"),
    path("clear/", views.plan_clear, name="clear"),
    path("items/<int:item_id>/remove/", views.plan_remove, name="remove"),
    path("items/<int:item_id>/move/", views.plan_move, name="move"),
    path("items/<int:item_id>/time/", views.plan_set_time, name="set_time"),
]
