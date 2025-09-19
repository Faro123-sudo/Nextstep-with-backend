# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Tag, Skill, Career, Resource, Multimedia,
    SuccessStory, UserProfile, Feedback,
    Quiz, QuizQuestion, QuizAttempt, Interaction
)

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name")

class CareerSerializer(serializers.ModelSerializer):
    required_skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), required=False)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Career
        fields = (
            "id", "domain", "title", "description", "required_skills",
            "education_path", "expected_salary", "tags", "popularity",
            "content_text", "embedding_id", "created_at", "updated_at"
        )
        read_only_fields = ("created_at", "updated_at")

class ResourceSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Resource
        fields = ("id","title","category","description","file","tags","views_count","created_by","created_at","content_text","embedding_id")
        read_only_fields = ("views_count","created_by","created_at")

class MultimediaSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Multimedia
        fields = ("id","title","type","url","uploaded_file","tags","transcript","rating_avg","rating_count","created_by","created_at","content_text","embedding_id")
        read_only_fields = ("rating_avg","rating_count","created_by","created_at")

class SuccessStorySerializer(serializers.ModelSerializer):
    submitted_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SuccessStory
        fields = ("id","title","domain","story_text","image","submitted_by","approved_by","approved_at","submitted_at","is_approved","content_text","embedding_id")
        read_only_fields = ("submitted_by","approved_by","approved_at","submitted_at")

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    interests = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = ("id","user","education_level","interests","profile_image","bio","updated_at")
        read_only_fields = ("user","updated_at")

class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    handled_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = ("id","user","category","message","status","submitted_at","handled_by")
        read_only_fields = ("user","submitted_at","handled_by")

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ("id","quiz","question_text","type","options","correct_answer","weightage")

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id","title","description","is_active","created_at","questions")
        read_only_fields = ("created_at","questions")

class QuizAttemptSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ("id","user","quiz","score","started_at","completed_at","answers")
        read_only_fields = ("user","started_at")

class InteractionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    content_type = serializers.StringRelatedField(read_only=True)
    # for creation we accept content_type_id and object_id
    content_type_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Interaction
        fields = ("id","user","content_type","object_id","interaction_type","metadata","created_at","content_type_id")
        read_only_fields = ("user","content_type","created_at")
