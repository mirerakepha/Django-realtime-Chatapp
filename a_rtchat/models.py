from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True)
    users_online = models.ManyToManyField(User, related_name="users_online", blank=True)

    def __str__(self):
        return self.group_name



class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='chat_messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} : {self.body}'


    class Meta:
        ordering = ['created']
