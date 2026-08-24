from django.urls import path
from .views import (
    CareerRecommendationView,
    CareerDetailRecommendationView,
    CareerSearchView,
    ResourceLibraryGenerateView,
    ResourceSearchView,
)

urlpatterns = [
    path('recommend/', CareerRecommendationView.as_view(), name='career-recommendation'),
    path('recommend-detail/', CareerDetailRecommendationView.as_view(), name='career-detail-recommendation'),
    path('search/', CareerSearchView.as_view(), name='career-search'),
    path('resources/generate/', ResourceLibraryGenerateView.as_view(), name='resource-library-generate'),
    path('resources/search/', ResourceSearchView.as_view(), name='resource-search'),
]
