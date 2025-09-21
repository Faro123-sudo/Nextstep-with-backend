from django.contrib import admin
from .models import (
    Tag, Skill, Career, Resource, Multimedia,
    SuccessStory, UserProfile, Feedback,
    Quiz, QuizQuestion, QuizAttempt,
    Interaction
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class SkillInline(admin.TabularInline):
    model = Career.required_skills.through
    extra = 1


class TagInline(admin.TabularInline):
    model = Career.tags.through
    extra = 1


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("title", "domain", "expected_salary", "popularity", "created_at")
    list_filter = ("domain", "created_at")
    search_fields = ("title", "description", "domain")
    inlines = [SkillInline, TagInline]
    readonly_fields = ("created_at", "updated_at", "content_text")
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        obj.build_content_text()
        super().save_model(request, obj, form, change)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "views_count", "created_by", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("content_text",)

    def save_model(self, request, obj, form, change):
        obj.build_content_text()
        super().save_model(request, obj, form, change)


@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "rating_avg", "rating_count", "created_by", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("title", "transcript")
    readonly_fields = ("content_text",)

    def save_model(self, request, obj, form, change):
        obj.build_content_text()
        super().save_model(request, obj, form, change)


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("title", "domain", "submitted_by", "is_approved", "submitted_at")
    list_filter = ("is_approved", "domain", "submitted_at")
    search_fields = ("title", "story_text", "domain")
    readonly_fields = ("content_text",)

    def save_model(self, request, obj, form, change):
        obj.build_content_text()
        super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "education_level", "updated_at")
    list_filter = ("education_level", "updated_at")
    search_fields = ("user__username", "bio")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("category", "status", "user", "submitted_at")
    list_filter = ("category", "status", "submitted_at")
    search_fields = ("message",)


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    inlines = [QuizQuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "started_at", "completed_at")
    list_filter = ("quiz", "started_at", "completed_at")
    search_fields = ("user__username",)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "interaction_type", "content_type", "object_id", "created_at")
    list_filter = ("interaction_type", "created_at", "content_type")
    search_fields = ("user__username", "metadata")
    readonly_fields = ("created_at",)
