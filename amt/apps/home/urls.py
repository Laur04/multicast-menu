from django.conf.urls import url

from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^vlc/(?P<target>[a-z0-9._:]+)/$', views.vlc, name='vlc'),
]