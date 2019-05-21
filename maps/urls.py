from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url('download', views.download, name="download"),
    url('get_geojson', views.get_geojson, name="get_geojson"),
    url('images', views.images, name="images"),
    url(r'', views.default_map, name="default")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
