from django.urls import path

from . import views

app_name = "view"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.index, name="index"),
    path("show/<int:stream_id>/", views.detail, name="detail"),
    path("upvote_description/<int:description_id>/", views.upvote_description, name="upvote_description"),
    path("downvote_description/<int:description_id>/", views.downvote_description, name="downvote_description"),
    path("submit_description/<int:stream_id>/", views.submit_description, name="submit_description"),
    path("open/<int:stream_id>", views.open, name="open"),
    path("report_stream/<int:stream_id>/", views.report_stream, name="report_stream"),
]
