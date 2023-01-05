from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']


class Ticket(models.Model):
    HIGH_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    LOW_PRIORITY = 3

    PRIORITY_CHOICES = [
        (HIGH_PRIORITY, 'High'),
        (MEDIUM_PRIORITY, 'Medium'),
        (LOW_PRIORITY, 'Low'),
    ]

    ACTIVE_STATUS = 1
    PROCESSED_STATUS = 2
    REJECTED_STATUS = 3
    RESTORED_STATUS = 4
    COMPLETED_STATUS = 5

    STATUS_CHOICES = [
        (ACTIVE_STATUS, 'Active'),
        (PROCESSED_STATUS, 'Processed'),
        (REJECTED_STATUS, 'Rejected'),
        (RESTORED_STATUS, 'Restored'),
        (COMPLETED_STATUS, 'Completed'),
    ]

    user = models.ForeignKey(CustomUser, related_name='tickets', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=MEDIUM_PRIORITY)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE_STATUS)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'

    def __str__(self):
        return self.title


class Comment(models.Model):
    DISCUSSION_TOPIC = 1
    REJECT_TOPIC = 2
    RESTORE_TOPIC = 3

    TOPIC_CHOICES = [
        (DISCUSSION_TOPIC, 'Discussion'),
        (REJECT_TOPIC, 'Reject'),
        (RESTORE_TOPIC, 'Restore'),
    ]

    author = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    topic = models.PositiveSmallIntegerField(choices=TOPIC_CHOICES, default=DISCUSSION_TOPIC)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ticket', 'created']
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.body
