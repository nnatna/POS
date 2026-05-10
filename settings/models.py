from django.db import models
from POS.image_utils import convert_uploaded_image_to_png


def profile_avatar_upload_to(instance, filename):
    return f'avatars/avatar{instance.user_id}.png'


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=32, blank=True)
    dob = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to=profile_avatar_upload_to, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk and self.avatar:
            old_avatar = Profile.objects.filter(pk=self.pk).values_list('avatar', flat=True).first()
            if not getattr(self.avatar, '_committed', False):
                self.avatar = convert_uploaded_image_to_png(self.avatar, f'avatar{self.user_id}.png')

            new_avatar_name = getattr(self.avatar, 'name', '')
            if old_avatar and old_avatar != new_avatar_name:
                self.avatar.storage.delete(old_avatar)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class OpeningHours(models.Model):
    day_of_week = models.CharField(max_length=10)
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.open_time} - {self.close_time}"
