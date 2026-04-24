from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.asset_list, name="asset_list"),
    path("asset/<str:asset_id>/", views.board, name="board"),
    path("asset/<str:asset_id>/post/new/", views.post_create, name="post_create"),
    path("asset/<str:asset_id>/post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("asset/<str:asset_id>/post/<int:post_id>/edit/", views.post_update, name="post_update"),
    path("asset/<str:asset_id>/post/<int:post_id>/delete/", views.post_delete, name="post_delete"),
]
