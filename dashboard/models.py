from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from crum import get_current_user


class UserProfile(models.Model):
    IMAGE_MAX_SIZE = (150, 150)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)
    job_title = models.CharField('intitulé de poste', max_length=500, blank=True)
    service = models.CharField('service', max_length=100, blank=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def resize_image(self):
        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()

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


class Contract(models.Model):
    code = models.CharField('code document', max_length=100, blank=True)
    service = models.CharField('service', max_length=100, blank=True)
    nature = models.CharField('nature du document', max_length=1000, blank=True)
    object = models.TextField('object du documnet', blank=True)
    supplier = models.CharField('fournisseur', max_length=500, blank=True)
    site = models.CharField('site', max_length=100, blank=True)
    end_date = models.DateField('date fin', null=True, blank=True)
    is_active = models.BooleanField('contrat actif', default=False)
    renew_date = models.DateField('date prévenance', null=True, blank=True)

    class Meta:
        verbose_name = "Contrat"
        ordering = ['id']

    def __str__(self):
        return self.code


class SuggestBox(models.Model):
    STATUS_CHOICES = [
        ('En Attente', 'En Attente'), ('En Cours', 'En Cours'), ('Terminée', 'Terminée'), ('Abandonnée', 'Abandonnée')
    ]

    title = models.CharField('titre', max_length=200)
    description = models.TextField('description', max_length=5000)
    objective = models.TextField('objectif', max_length=1000, blank=True)
    status = models.CharField('statut', max_length=20, choices=STATUS_CHOICES, default='En Attente')
    created_at = models.DateTimeField('créer le', editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="suggests_created", editable=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Boite à idée"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
