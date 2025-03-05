from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.CharField(max_length=255, default="What is your favorite movie")
    security_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        # Always set the security question to the hardcoded value
        self.security_question = "What is your favorite movie"
        # Get the answer from user's first_name
        self.security_answer = self.user.first_name
        super().save(*args, **kwargs)