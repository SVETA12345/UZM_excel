from django.contrib import admin

from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Управление замерами API",
      default_version='v1',
      description="Swagger для управления замерами.",
      terms_of_service="http://portal.corp.igirgi.su/",
      contact=openapi.Contact(email="DovidenkovAL@igirgi.rosneft.ru"),
      license=openapi.License(name=""),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', include('news.urls')),
    path('axes/', include('excel_parcer.urls')),
    path('admin/', admin.site.urls, name="admin"),
    path('report/', include('report.urls')),
    path('main_data/', include('Field.urls')),
    path('data_handler/', include('data_handler.urls')),
    # SWAGGER
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
