from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from crum import get_current_user

from squalaetp.models import Xelon
from utils.file.export import calibre


class TagXelon(models.Model):
    xelon = models.CharField(max_length=10)
    comments = models.CharField('commentaires', max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if calibre.check(self.xelon):
            raise ValidationError(_('CALIBRE file exists !'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        calibre.file(self.xelon, self.comments, user)
        super(TagXelon, self).save(*args, **kwargs)

    def __str__(self):
        return self.xelon


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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    validation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        super(CsdSoftware, self).save(*args, **kwargs)

    def __str__(self):
        return self.jig


class ThermalChamber(models.Model):
    CHOICES = [('FROID', 'FROID'), ('CHAUD', 'CHAUD')]

    operating_mode = models.CharField('mode de fonctionnement', max_length=20, choices=CHOICES)
    xelon_number = models.CharField('N° Xelon', max_length=10, blank=True)
    start_time = models.DateTimeField('heure de début', blank=True, null=True)
    stop_time = models.DateTimeField('heure de fin', blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user:
            self.created_by = user
        super(ThermalChamber, self).save(*args, **kwargs)

    def __str__(self):
        first_name, last_name = self.created_by.first_name, self.created_by.last_name
        if first_name and last_name:
            return "{} {} - {}".format(self.created_by.last_name, self.created_by.first_name, self.xelon_number)
        else:
            return "{} - {}".format(self.created_by.username, self.xelon_number)


class EtudeProject(models.Model):
    name = models.CharField('projet', max_length=200)
    progress = models.PositiveIntegerField('avancée en %', validators=[MaxValueValidator(100), MinValueValidator(0)])

    def __str__(self):
        return self.name


class Suptech(models.Model):
    date = models.DateField('DATE')
    user = models.CharField('QUI', max_length=50)
    xelon = models.CharField('XELON', max_length=10, blank=True)
    item = models.CharField('ITEM', max_length=200)
    time = models.CharField('TIME', max_length=50)
    info = models.TextField('INFO', max_length=5000)
    rmq = models.TextField('RMQ', max_length=5000, blank=True)
    action = models.TextField('ACTION/RETOUR', max_length=5000, blank=True)

    class Meta:
        verbose_name = "Logs SupTech"
        ordering = ['pk']

    def __str__(self):
        return self.item
