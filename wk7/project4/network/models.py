from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

class Post(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"{self.creator.username}: {self.content[:30]}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
