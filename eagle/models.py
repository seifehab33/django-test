
from django.conf import settings
import os
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Location(models.Model):
    name = models.CharField(max_length=255)


class Camera(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)


def get_photo_path(instance, filename):
    if not instance.id:
        raise ValueError(
            "The instance must be saved to generate an ID before calling get_photo_path.")

    ext = filename.split('.')[-1]
    directory = f"{instance.first_name}_{instance.id}"
    filename = f"{directory}.{ext}"
    return os.path.join('photos', directory, filename)


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=254)
    photo = models.ImageField(upload_to=get_photo_path)

    username = models.CharField(
        max_length=150, null=False, blank=False, unique=True)
    password = models.CharField(max_length=128, null=False, blank=False)

    def photo_url(self):
        if self.photo:
            return self.photo.url
        else:
            return None

    def save(self, *args, **kwargs):
        # Check if creating a new instance; if so, temporarily save without the photo
        if not self.id:  # No ID means the instance is not saved yet (it's new)
            photo_file = self.photo
            self.photo = None  # Temporarily remove the photo
            super().save(*args, **kwargs)  # Save, so the instance gets an ID
            self.photo = photo_file

        if not self.photo:
            raise ValueError("Photo field cannot be empty")
        if self.password:
            self.password = make_password(self.password)
        # For new and existing instances, re-save with the photo now that we have an ID
        super().save(*args, **kwargs)


class Community(models.Model):
    users = models.ManyToManyField(Person, through='UsersInCommunity')
    Community_ID = models.AutoField(primary_key=True)


class UsersInCommunity(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    Community_ID = models.ForeignKey(Community, on_delete=models.CASCADE)
    join_date = models.DateField()


class Camera_History(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    checkIn_time = models.DateTimeField()
    checkOut_time = models.DateTimeField()


class SecurityPersonnel(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class Admin(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    birth_date = models.DateField()

    # Add username and password fields
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to='admin_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.password)


class AdminLoginHistory(models.Model):
    admin = models.ForeignKey(Admin,
                              on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-login_time']


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phoneno = models.IntegerField()
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
