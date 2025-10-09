import os
from os.path import basename

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model
import shortuuid

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True, default=shortuuid.uuid)#->pip install shortuuid
    groupchat_name = models.CharField(max_length=100, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True,  on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name="online_in_groups", blank=True, )
    members = models.ManyToManyField(User, related_name="chat_groups", blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name



class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='chat_messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return basename(self.file.name)
        else:
            return None


    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'


    class Meta:
        ordering = ['created']


    @property
    def is_image(self):
        if self.filename.lower().endswith(('.png', '.jpeg', '.jpg', '.gif', '.svg', '.webp')):
            return True
        else:
            return False
