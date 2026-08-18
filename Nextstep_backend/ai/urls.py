from django.urls import path
from .views import (
    CareerRecommendationView,
    CareerDetailRecommendationView,
    CareerSearchView,
)

urlpatterns = [
    path('recommend/', CareerRecommendationView.as_view(), name='career-recommendation'),
    path('recommend-detail/', CareerDetailRecommendationView.as_view(), name='career-detail-recommendation'),
    path('search/', CareerSearchView.as_view(), name='career-search'),
]
