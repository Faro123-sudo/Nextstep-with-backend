# models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

# For generic FK used by Interaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


# Career bank (Careers)
class Career(models.Model):
    domain = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name="careers")
    education_path = models.TextField(blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="careers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    popularity = models.IntegerField(default=0)  # could track views or recommendation score

    # denormalized field used to build embeddings / semantic text quickly
    content_text = models.TextField(blank=True, help_text="Denormalized text for embeddings/search")
    # optional: pointer to embedding storage (external vector DB id) or local embedding key
    embedding_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["domain"]),
        ]

    def __str__(self):
        return self.title

    def build_content_text(self):
        parts = [
            self.title or "",
            self.description or "",
            " ".join([t.name for t in self.tags.all()]) if hasattr(self, "tags") else "",
            " ".join([s.name for s in self.required_skills.all()]) if hasattr(self, "required_skills") else "",
        ]
        self.content_text = " | ".join([p.strip() for p in parts if p])
        return self.content_text


# Resources (documents, pdfs, etc.)
class Resource(models.Model):
    CATEGORY_CHOICES = [
        ("guide", "Guide"),
        ("infographic", "Infographic"),
        ("pdf", "PDF"),
        ("slides", "Slides"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="other")
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/")
    tags = models.ManyToManyField(Tag, blank=True, related_name="resources")
    views_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="resources")
    created_at = models.DateTimeField(auto_now_add=True)

    # denormalized text for embeddings / search
    content_text = models.TextField(blank=True, help_text="Denormalized text for embeddings/search")
    embedding_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    def build_content_text(self):
        parts = [self.title or "", self.description or "", " ".join([t.name for t in self.tags.all()])]
        self.content_text = " | ".join([p.strip() for p in parts if p])
        return self.content_text


# Multimedia content (videos, podcasts, images)
class Multimedia(models.Model):
    TYPE_CHOICES = [
        ("video", "Video"),
        ("audio", "Audio"),
        ("image", "Image"),
        ("article", "Article"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)  # remote link or streaming url
    uploaded_file = models.FileField(upload_to="multimedia/", blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="multimedia")
    transcript = models.TextField(blank=True)
    rating_avg = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="multimedia")

    # denormalized text for embeddings / search
    content_text = models.TextField(blank=True, help_text="Denormalized text for embeddings/search")
    embedding_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.type})"

    def build_content_text(self):
        parts = [self.title or "", self.transcript or "", " ".join([t.name for t in self.tags.all()])]
        self.content_text = " | ".join([p.strip() for p in parts if p])
        return self.content_text


# Success Stories
class SuccessStory(models.Model):
    title = models.CharField(max_length=255)  # rname from ER = name/title
    domain = models.CharField(max_length=120, blank=True, null=True)
    story_text = models.TextField()
    image = models.ImageField(upload_to="success_stories/", blank=True, null=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="success_stories")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_stories")
    approved_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    # denormalized text for embeddings / search
    content_text = models.TextField(blank=True, help_text="Denormalized text for embeddings/search")
    embedding_id = models.CharField(max_length=255, blank=True, null=True)

    def approve(self, approver):
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.is_approved = True
        self.save()

    def __str__(self):
        return self.title

    def build_content_text(self):
        parts = [self.title or "", self.story_text or "", self.domain or ""]
        self.content_text = " | ".join([p.strip() for p in parts if p])
        return self.content_text



class UserProfile(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ("none", "None"),
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("diploma", "Diploma"),
        ("bachelors", "Bachelors"),
        ("masters", "Masters"),
        ("phd", "PhD"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    education_level = models.CharField(max_length=40, choices=EDUCATION_LEVEL_CHOICES, default="other")
    interests = models.ManyToManyField(Tag, blank=True, related_name="interested_users")
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


# Feedback
class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ("bug", "Bug"),
        ("suggestion", "Suggestion"),
        ("query", "Query"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
        ("resolved", "Resolved"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedbacks")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    message = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    submitted_at = models.DateTimeField(auto_now_add=True)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="handled_feedbacks")

    def __str__(self):
        return f"{self.category} - {self.status}"


# Quiz system (simple)
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    TYPE_CHOICES = [
        ("mcq", "Multiple Choice"),
        ("text", "Text/Long answer"),
        ("likert", "Likert scale"),
        ("slider", "Slider"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="mcq")
    # options for MCQ stored as JSON: [{"id":"a","text":"Option A"}, ...]
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.CharField(max_length=255, blank=True, null=True)  # evaluation logic can vary
    weightage = models.FloatField(default=1.0)

    def __str__(self):
        return f"Q: {self.question_text[:60]}"


# Optional: store quiz attempts/answers
class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    answers = models.JSONField(blank=True, null=True)  # {"question_id": "selected_option", ...}

    def __str__(self):
        return f"{self.user} - {self.quiz} ({self.score})"


# Interaction model for events (views/likes/saves/etc.)
class Interaction(models.Model):
    INTERACTION_CHOICES = [
        ("view", "View"),
        ("like", "Like"),
        ("save", "Save"),
        ("apply", "Apply"),
        ("share", "Share"),
        ("dismiss", "Dismiss"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interactions")
    # Generic relationship so you can record interactions for any model instance
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    metadata = models.JSONField(blank=True, null=True, help_text='Arbitrary event metadata, e.g. {"duration": 12.5, "session":"abc", "device":"mobile"}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "interaction_type", "created_at"]),
            models.Index(fields=["content_type", "object_id", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.interaction_type} - {self.content_type}({self.object_id})"
