from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):

    email = models.EmailField()

    ROLE_CHOICES = [

        ('user', 'User'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),

    ]

    role = models.CharField(

        max_length=20,
        choices=ROLE_CHOICES,
        default='user'

    )

    def __str__(self):

        return self.username



class Ticket(models.Model):

    STATUS_CHOICES = [

        ('new', 'Новое'),

        ('in_progress', 'В обработке'),

        ('done', 'Завершено'),

    ]

    PRIORITY_CHOICES = [

        ('low', 'Low'),

        ('medium', 'Medium'),

        ('high', 'High'),

        ('critical', 'Critical'),

    ]

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE

    )

    text = models.TextField()

    predicted_category = models.CharField(

        max_length=255

    )

    confidence = models.FloatField(

        default=0
    )

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='new'

    )

    priority = models.CharField(

        max_length=20,

        choices=PRIORITY_CHOICES,

        default='medium'

    )

    admin_comment = models.TextField(

        blank=True,

        null=True

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return f'#{self.id} - {self.predicted_category}'