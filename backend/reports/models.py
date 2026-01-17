from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    max_posts = models.IntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    insights = JSONField(default=list, blank=True)
    metrics = JSONField(default=dict, blank=True)
    recommendations = JSONField(default=list, blank=True)

    def __str__(self):
        return f"Report {self.id} for {self.user.username} ({self.status})"
