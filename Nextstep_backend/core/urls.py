# core/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r"tags", views.TagViewSet, basename="tag")
router.register(r"skills", views.SkillViewSet, basename="skill")
router.register(r"careers", views.CareerViewSet, basename="career")
router.register(r"resources", views.ResourceViewSet, basename="resource")
router.register(r"multimedia", views.MultimediaViewSet, basename="multimedia")
router.register(r"success-stories", views.SuccessStoryViewSet, basename="successstory")
router.register(r"feedback", views.FeedbackViewSet, basename="feedback")
router.register(r"quizzes", views.QuizViewSet, basename="quiz")
router.register(r"quiz-questions", views.QuizQuestionViewSet, basename="quizquestion")
router.register(r"quiz-attempts", views.QuizAttemptViewSet, basename="quizattempt")
router.register(r"interactions", views.InteractionViewSet, basename="interaction")
# profile is a single endpoint
urlpatterns = [
    path("", include(router.urls)),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
]
