from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.seo_views import robots_txt_view, sitemap_xml_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt_view, name='robots-txt'),
    path('sitemap.xml', sitemap_xml_view, name='sitemap-xml'),
    path('api/v1/', include('core.urls')),
    path('api/v1/', include('localization.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
