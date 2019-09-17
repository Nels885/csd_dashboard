from model_utils import FieldTracker
from PIL import Image
from datetime import date
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    # Here we instantiate a FieldTracker to track any fields specially image field
    tracker = FieldTracker()

    def save(self, *args, **kwargs):
        super().save()

        """
        We get here the self avatar condition
        in case of there is no self.image as example
        after a clear action.
        """
        print(self.image)
        if self.image and self.tracker.has_changed('image'):
            print(self.tracker.previous('image'))
            # keep the upload image path in order to delete if after
            upload_image = self.image.path

            # rename avatar image
            image_name = '{}-{}.jpg'.format(date.today(), self.user.id)

            img = Image.open(upload_image)

            # convert all picture to jpg
            img = img.convert('RGB')

            # resize picture
            img = img.resize((140,140), Image.ANTIALIAS)

            # make readable picture
            output = BytesIO()
            img.save(output, format='JPEG', quality=100)
            output.seek(0)
            self.image = InMemoryUploadedFile(output,
                                              'ImageField',
                                              image_name,
                                              'image/jpeg',
                                              sys.getsizeof(output),
                                              None)

            super(UserProfile, self).save()

            # delete the upload of image before resize it
            if 'default.png' not in upload_image:
                os.remove(upload_image)

                # delete old image file
                if self.image and self.tracker.previous('image'):
                    try:
                        old_image = '{}/{}'.format(settings.MEDIA_ROOT, self.tracker.previous('image'))
                        print(old_image)
                        os.remove(old_image)
                    except FileNotFoundError:
                        pass

    def __str__(self):
        return self.user.username


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class CsdSoftware(models.Model):

    STATUS_CHOICES = [
        ('Validé', 'Validé'),
        ('En test', 'En test'),
        ('Etudes', 'Etudes'),
        ('Abandonné', 'Abandonné'),
        ('PDI Only', 'PDI Only')
    ]

    jig = models.CharField(max_length=100)
    new_version = models.CharField(max_length=20)
    old_version = models.CharField(max_length=20, null=True, blank=True)
    link_download = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    validation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.jig
