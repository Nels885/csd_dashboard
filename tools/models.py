from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from crum import get_current_user

from constance import config

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


class ThermalChamberMeasure(models.Model):
    datetime = models.DateTimeField('heure de mesure', auto_now_add=True)
    value = models.IntegerField('valeur mesuré')
    temp = models.CharField('température', max_length=20)

    class Meta:
        verbose_name = "Thermal Chamber Measure"
        ordering = ['-datetime']

    def __str__(self):
        return self.datetime.strftime("%d/%m/%Y %H:%M")


class EtudeProject(models.Model):
    name = models.CharField('projet', max_length=200)
    progress = models.PositiveIntegerField('avancée en %', validators=[MaxValueValidator(100), MinValueValidator(0)])

    def __str__(self):
        return self.name


class Suptech(models.Model):
    STATUS_CHOICES = [
        ('En Attente', 'En Attente'), ('En Cours', 'En Cours'), ('Cloturée', 'Cloturée'), ('Annulée', 'Annulée')
    ]

    date = models.DateField('DATE')
    user = models.CharField('QUI', max_length=50)
    xelon = models.CharField('XELON', max_length=10, blank=True)
    item = models.CharField('ITEM', max_length=200)
    time = models.CharField('TIME', max_length=10)
    info = models.TextField('INFO', max_length=2000)
    rmq = models.TextField('RMQ', max_length=2000, blank=True)
    action = models.TextField('ACTION/RETOUR', max_length=2000, blank=True)
    status = models.TextField('STATUT', max_length=50, default='En Attente', choices=STATUS_CHOICES)
    deadline = models.DateField('DATE LIMITE', null=True, blank=True)
    created_at = models.DateTimeField('ajouté le', editable=False, null=True)
    created_by = models.ForeignKey(User, related_name="suptechs_created", editable=False, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    modified_at = models.DateTimeField('modifié le', null=True)
    modified_by = models.ForeignKey(User, related_name="suptechs_modified", on_delete=models.SET_NULL, null=True,
                                    blank=True)

    class Meta:
        verbose_name = "SupTech Log"
        ordering = ['pk']

    def __str__(self):
        return self.item


class SuptechItem(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    extra = models.BooleanField(default=False)
    mailing_list = models.TextField("Liste d'email", max_length=5000, default=config.SUPTECH_TO_EMAIL_LIST)

    class Meta:
        verbose_name = "SupTech Item"
        ordering = ['name']

    def __str__(self):
        return self.name


class BgaTime(models.Model):
    name = models.CharField('Nom de la machine', max_length=100)
    date = models.DateField('date', auto_now_add=True)
    start_time = models.TimeField('heure de START', auto_now_add=True)
    end_time = models.TimeField('heure de FIN', null=True)
    duration = models.IntegerField('durée en secondes', null=True)

    class Meta:
        verbose_name = "BGA Time"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        status = kwargs.pop('status', None)
        if status:
            if self.pk and status.upper() == "STOP":
                self.end_time = timezone.localtime().time()
            elif self.pk and status.upper() == "START":
                date_time = timezone.datetime.combine(self.date, self.start_time)
                self.end_time = (date_time + timezone.timedelta(minutes=5)).time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.date} {self.start_time}"
