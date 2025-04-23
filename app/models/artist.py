from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name