# backend/insights/models.py

from django.db import models

class PostInsight(models.Model):
    post_id = models.CharField(max_length=200, unique=True)
    user_id = models.CharField(max_length=200)
    original_text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    sentiment = models.CharField(max_length=50, default="neutral")
    is_respectful = models.BooleanField(default=True)
    mentions_location = models.CharField(max_length=200, blank=True, null=True)
    privacy_disclosure = models.BooleanField(default=False)
    toxic = models.BooleanField(default=False)
    misinformation_risk = models.BooleanField(default=False)
    status_type = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.post_id} - {self.sentiment}"
