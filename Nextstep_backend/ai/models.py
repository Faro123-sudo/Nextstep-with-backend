from django.db import models
from django.conf import settings


class AIRecommendation(models.Model):
    """
    Persisted AI-generated career recommendations and search results.

    Used as a durable cache layer so identical AI requests don't consume
    Gemini tokens.  The Django cache layer (locmem / Redis) provides the
    fast path; this model provides the durable fallback.
    """

    RECOMMENDATION_TYPE_CHOICES = [
        ("quiz", "Quiz-based recommendation"),
        ("career_detail", "Per-career detail recommendation"),
        ("search", "Free-text career search"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_recommendations",
    )
    career = models.ForeignKey(
        "core.Career",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_recommendations",
    )
    recommendation_type = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_TYPE_CHOICES,
        default="search",
    )
    input_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="MD5 hash of the canonicalised input — used for deduplication.",
    )
    input_data = models.JSONField(
        blank=True,
        default=dict,
        help_text="Original request payload (query, career data, quiz responses).",
    )
    output_data = models.JSONField(
        blank=True,
        default=dict,
        help_text="Structured AI response.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["recommendation_type", "input_hash"]),
            models.Index(fields=["career", "recommendation_type"]),
        ]

    def __str__(self):
        return f"AIRecommendation({self.recommendation_type}) — {self.input_hash[:12]}"