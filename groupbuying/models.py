from django.db import models
from django.contrib.auth.models import User

class UserItem(models.Model):
    text = models.CharField(max_length=200)
    profile_picture = models.FileField(blank=True)
    bio_input_text = models.TextField(max_length=500)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    cell_phone = models.CharField(max_length=16)
    address = models.CharField(max_length=200)
    followers = models.ManyToManyField(User)
    # content_type = models.CharField(max_length=50)
    # ip_addr = models.GenericIPAddressField()
    # storage_path = models.FileField()

    def __str__(self):
        return 'id=' + str(self.id) + ',first_name="' + self.first_name + 'last_name' + self.last_name