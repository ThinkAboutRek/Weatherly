from django.db import models
from django.contrib.auth.models import User


class Search(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='searches',
    )
    city = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.city} at {self.searched_at:%Y-%m-%d %H:%M}"
