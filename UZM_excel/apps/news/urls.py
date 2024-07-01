from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import index_page


urlpatterns = [
    path('', index_page, name="index_page")
]

if settings.DEBUG:
    # urlpatterns = [
    #     path("__debug__/", include("debug_toolbar.urls")),
    # ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
