from django.urls import path

from . import views

app_name = 'view'

urlpatterns = [
    path('', views.index, name='index'),
    path('downvote/<target>/', views.downvote, name='downvote'),
    path('show/<target>/', views.show_video, name='show_video'),
    path('show/<target>/<os>/', views.vlc, name='vlc'),
    path('invalid-streams/', views.invalid_streams, name="invalid_streams"),
]
