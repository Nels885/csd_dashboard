from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from crum import get_current_user


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)
    job_title = models.CharField('intitulé de poste', max_length=500, blank=True)
    service = models.CharField('service', max_length=100, blank=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return self.user.username


class ShowCollapse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    general = models.BooleanField('informations générales', default=False)
    motor = models.BooleanField('alimentation moteur', default=False)
    axle = models.BooleanField('suspension direction freinage', default=False)
    body = models.BooleanField('carrosserie équipements', default=False)
    interior = models.BooleanField('equipements intérieur', default=False)
    electric = models.BooleanField('électricité', default=False)
    diverse = models.BooleanField('divers', default=False)

    class Meta:
        verbose_name = "Affichage detail"

    def __str__(self):
        return self.user.username


class Post(models.Model):
    title = models.CharField('titre', max_length=100)
    overview = RichTextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.author = user
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class WebLink(models.Model):
    WEB_LINK_TYPE_CHOICES = [
        ('PSA', 'PSA'), ('OPEL', 'OPEL'), ('FORD', 'FORD'), ('RENAULT', 'RENAULT'), ('CLARION', 'CLARION'),
        ('VAG', 'VAG'), ('PARTS_SUPPLIERS', 'PARTS_SUPPLIERS'), ('AUTRES', 'AUTRES')
    ]

    title = models.CharField('titre', max_length=200)
    url = models.URLField('lien web')
    type = models.CharField('type', max_length=50, choices=WEB_LINK_TYPE_CHOICES)
    description = models.TextField('description', max_length=2000)
    thumbnail = models.ImageField(default="no-img_160x120.png", upload_to="link_thumbnail")

    def __str__(self):
        return self.title
