from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "NearbyGo administration"
admin.site.site_title = "NearbyGo admin"
admin.site.index_title = "Manage categories and places"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("plan/", include("planner.urls")),
    path("", include("places.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
