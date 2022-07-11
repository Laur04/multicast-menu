from django.urls import path

from . import views

app_name = "view"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.index, name="index"),
    path("detail/<int:stream_id>/", views.detail, name="detail"),
    path("detail/open/<int:stream_id>/", views.open, name="open"),
    path("detail/report/<int:stream_id>/", views.report, name="report"),
    path("description/upvote/<int:description_id>/", views.upvote_description, name="upvote_description"),
    path("description/downvote/<int:description_id>/", views.downvote_description, name="downvote_description"),
    path("description/submit/<int:stream_id>/", views.submit_description, name="submit_description"),
    path("broken/", views.broken_index, name="broken_index"),
    path("broken/detail/<int:stream_id>/", views.broken_detail, name="broken_detail"),
    path("broken/clear/<int:stream_id>/", views.broken_clear, name="broken_clear"),
    path("detail/set_editors_choice/<int:stream_id>/", views.set_editors_choice, name="set_editors_choice"),
    path("detail/like_stream/<int:stream_id>/", views.like_stream, name="like_stream"),
    path("detail/remove_like_from_stream/<int:stream_id>/", views.remove_like_from_stream, name="remove_like_from_stream"),
]
