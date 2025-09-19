# core/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from .models import (
    Tag, Skill, Career, Resource, Multimedia,
    SuccessStory, UserProfile, Feedback,
    Quiz, QuizQuestion, QuizAttempt, Interaction
)
from .serializers import (
    TagSerializer, SkillSerializer, CareerSerializer, ResourceSerializer,
    MultimediaSerializer, SuccessStorySerializer, UserProfileSerializer,
    FeedbackSerializer, QuizSerializer, QuizQuestionSerializer,
    QuizAttemptSerializer, InteractionSerializer
)

# Permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: object-level write permission only to owners.
    Assumes model has `created_by` or `submitted_by` FK to user.
    """
    def has_object_permission(self, request, view, obj):
        # read-only allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # owners can edit/delete
        owner = getattr(obj, "created_by", None) or getattr(obj, "submitted_by", None)
        if owner is None:
            # fall back to staff-only edits
            return request.user and request.user.is_staff
        return owner == request.user or request.user.is_staff

# Simple CRUD viewsets
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "id"]

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]

class CareerViewSet(viewsets.ModelViewSet):
    queryset = Career.objects.all().prefetch_related("tags","required_skills")
    serializer_class = CareerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["domain", "tags", "required_skills"]
    search_fields = ["title", "description", "domain"]
    ordering_fields = ["created_at","popularity","expected_salary"]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def build_content_text(self, request, pk=None):
        """Admin-only: rebuild denormalized content_text for this career instance"""
        obj = self.get_object()
        obj.build_content_text()
        obj.save(update_fields=["content_text"])
        return Response({"detail": "content_text rebuilt", "content_text": obj.content_text})

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all().prefetch_related("tags")
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category","tags"]
    search_fields = ["title","description"]
    ordering_fields = ["created_at","views_count"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def build_content_text(self, request, pk=None):
        obj = self.get_object()
        obj.build_content_text()
        obj.save(update_fields=["content_text"])
        return Response({"detail":"content_text rebuilt","content_text":obj.content_text})

class MultimediaViewSet(viewsets.ModelViewSet):
    queryset = Multimedia.objects.all().prefetch_related("tags")
    serializer_class = MultimediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["type","tags"]
    search_fields = ["title","transcript"]
    ordering_fields = ["created_at","rating_avg"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def build_content_text(self, request, pk=None):
        obj = self.get_object()
        obj.build_content_text()
        obj.save(update_fields=["content_text"])
        return Response({"detail":"content_text rebuilt","content_text":obj.content_text})

class SuccessStoryViewSet(viewsets.ModelViewSet):
    queryset = SuccessStory.objects.all()
    serializer_class = SuccessStorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title","story_text","domain"]
    ordering_fields = ["submitted_at","is_approved"]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        story = self.get_object()
        story.approve(request.user)
        return Response({"detail":"approved","approved_at":story.approved_at})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def build_content_text(self, request, pk=None):
        obj = self.get_object()
        obj.build_content_text()
        obj.save(update_fields=["content_text"])
        return Response({"detail":"content_text rebuilt","content_text":obj.content_text})

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve / update the current user's profile.
    URL: /api/core/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().select_related("user","handled_by")
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["message"]
    ordering_fields = ["submitted_at","status"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title","description"]
    ordering_fields = ["created_at"]

class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]  # only authenticated users can attempt

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # users only see their attempts unless staff
        if self.request.user.is_staff:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(user=self.request.user)

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all().select_related("user")
    serializer_class = InteractionSerializer
    # create by authenticated users; listing restricted
    def get_permissions(self):
        if self.action in ("create",):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]  # list / retrieve / delete only for admins

    def perform_create(self, serializer):
        # accept content_type_id if provided
        ct_id = self.request.data.get("content_type_id")
        if ct_id:
            ct = get_object_or_404(ContentType, pk=ct_id)
            serializer.save(user=self.request.user, content_object=ct.get_object_for_this_type(pk=self.request.data.get("object_id")))
        else:
            # fallback: try to resolve by content_type string (not implemented) - simplest: direct save with object_id + content_type set
            # To create generic FK properly from client, send content_type_id
            serializer.save(user=self.request.user)
