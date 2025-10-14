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

from accounts.serializers import UserSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    # Nest the full user details for reading
    user = UserSerializer(read_only=True)
    interests = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    # Add fields to update the related User model
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        # These fields will be available for both reading and writing (unless in read_only_fields)
        fields = (
            "id", "user", "education_level", "interests", "profile_image",
            "bio", "updated_at", "first_name", "last_name", "email"
        )
        read_only_fields = ("id", "user", "updated_at")
    def update(self, instance, validated_data):
        """
        Update UserProfile instance and allow updating nested user fields
        (first_name, last_name, email) which are declared with dotted sources.

        Also handle many-to-many 'interests' and file field 'profile_image'.
        """
        # Pop nested user fields (they appear under the 'user' key because of source='user.xxx')
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            # Update only provided fields
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Handle interests (PrimaryKeyRelatedField many=True gives a list of Tag instances)
        interests = validated_data.pop('interests', None)
        if interests is not None:
            try:
                instance.interests.set(interests)
            except Exception:
                # swallow errors here; validation should have handled invalid ids
                pass

        # Handle file and simple fields
        for attr in ('profile_image', 'bio', 'education_level'):
            if attr in validated_data:
                setattr(instance, attr, validated_data.pop(attr))

        # Any remaining validated_data keys (if present) can be set generically
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            if request is not None:
                representation['profile_image'] = request.build_absolute_uri(instance.profile_image.url)
            else:
                representation['profile_image'] = instance.profile_image.url
        # If we have a nested `user` object in the representation, prefer it
        # as the authoritative source and remove top-level duplicate fields
        # that are also provided under `user`. This avoids redundancy such as
        # returning first_name/email/etc both at top-level and under user.
        if representation.get('user'):
            duplicate_keys = ['first_name', 'last_name', 'email', 'bio', 'education_level', 'interests']
            for k in duplicate_keys:
                if k in representation:
                    representation.pop(k, None)

        return representation

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
