from django.urls import path

from .views import RecordVisitAPIView, RecordVisitPixelView

urlpatterns = [
    path('analytics/visit/', RecordVisitAPIView.as_view(), name='analytics-visit'),
    path('analytics/visit/pixel.gif', RecordVisitPixelView.as_view(), name='analytics-visit-pixel'),
]
