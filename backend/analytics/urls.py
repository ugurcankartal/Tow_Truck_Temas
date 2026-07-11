from django.urls import path

from .views import RecordVisitAPIView

urlpatterns = [
    path('analytics/visit/', RecordVisitAPIView.as_view(), name='analytics-visit'),
]
