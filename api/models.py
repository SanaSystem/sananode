from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    phone = models.CharField(max_length=20)
    rsa_public_key = models.TextField()
    encrypted_rsa_private_key = models.TextField(blank=True, null=True)
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class MedBlock(models.Model):
    user = models.ForeignKey(User, models.CASCADE, 'medblocks')
    ipfs_hash = models.CharField(max_length=200, blank=True, null=True)
    format = models.CharField(max_length=200)
    path_to_data = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    last_synced = models.DateTimeField(blank=True, null=True)
    signature = models.CharField(max_length=500)

class Key(models.Model):
    medblock = models.ForeignKey(MedBlock, models.CASCADE, 'keys')
    rsa_public_key = models.TextField()
    encryption_key = models.TextField()