from django.conf.urls import url

from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^show/(?P<target>[a-z0-9._:]+)/$', views.show_video, name='show_video'),
    url(r'^show/(?P<target>[a-z0-9._:]+)/(?P<os>\w+)/$', views.vlc, name='vlc'),
    url(r'^contact/(?P<target>[a-z0-9._:]+)/$', views.contact, name='contact'),
]