from django.urls import path

from .seo_views import robots_txt_view, sitemap_xml_view
from .views import (
    APIRootView,
    ContactAPIView,
    SiteSettingsAPIView,
    TriggerRebuildAPIView,
)

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('site-settings/', SiteSettingsAPIView.as_view(), name='site-settings'),
    path('contact/', ContactAPIView.as_view(), name='contact'),
    path('trigger-rebuild/', TriggerRebuildAPIView.as_view(), name='trigger-rebuild'),
    path('robots.txt', robots_txt_view, name='api-robots-txt'),
    path('sitemap.xml', sitemap_xml_view, name='api-sitemap-xml'),
]
