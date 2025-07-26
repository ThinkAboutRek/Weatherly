from django.db import models

class Search(models.Model):
    city = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city} at {self.searched_at:%Y-%m-%d %H:%M}"
