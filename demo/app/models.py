from django.db import models
import couchsync


class Note(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

couchsync.register(Note)
