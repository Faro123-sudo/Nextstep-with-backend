from django.urls import path
from .views import CareerRecommendationView

urlpatterns = [
    path('recommend/', CareerRecommendationView.as_view(), name='career-recommendation'),
]
