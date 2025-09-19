from django.contrib.contenttypes.models import ContentType
from .models import Interaction, Career
from django.http import      request

career = Career.objects.first()
Interaction.objects.create(
    user=request.user,
    content_type=ContentType.objects.get_for_model(career),
    object_id=career.id,
    interaction_type="view",
    metadata={"duration_seconds": 12.5, "session": "abc123", "device": "mobile", "referrer": "/home"}
)
