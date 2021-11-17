from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = (
    [
    path("admin/", admin.site.urls),
    path("", include("django.contrib.auth.urls")),
    path("", include("multicast.apps.view.urls", namespace="view")),
    path("add/", include("multicast.apps.add.urls", namespace="add")),
    path("manage/", include("multicast.apps.manage.urls", namespace="manage")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
