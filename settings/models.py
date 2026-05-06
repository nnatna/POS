from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=32, blank=True)
    dob = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class OpeningHours(models.Model):
    day_of_week = models.CharField(max_length=10)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.open_time} - {self.close_time}"