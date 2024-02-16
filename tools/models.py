from collections import OrderedDict

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.template.loader import render_to_string
from django.core.validators import MaxValueValidator, MinValueValidator
from crum import get_current_user

from constance import config as conf

from .tasks import send_email_task
from squalaetp.models import Xelon
from utils.file.export import calibre, telecode
from utils.conf import string_to_list


class TagXelon(models.Model):
    CAL_CHOICES = ((False, _('CAL software')), (True, "Diagbox"))
    TEL_CHOICES = ((False, _('No')), (True, _("Yes")))

    xelon = models.CharField(max_length=10)
    comments = models.CharField('commentaires', max_length=400, blank=True)
    calibre = models.BooleanField('calibration', default=False, choices=CAL_CHOICES)
    telecode = models.BooleanField('télécodage', default=False, choices=TEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tag Xelon Multi"
        ordering = ['-created_at']

    def clean(self):
        try:
            telecode_tag = Xelon.objects.get(numero_de_dossier=self.xelon).telecodage
        except Xelon.DoesNotExist:
            telecode_tag = None
        if self.calibre and calibre.check(self.xelon):
            raise ValidationError(_('CALIBRE file exists !'))
        elif self.telecode and telecode.check(self.xelon):
            raise ValidationError(_('TELECODE file exists !'))
        elif not self.telecode and telecode_tag == '1':
            raise ValidationError(_('TELECODE is required !'))
        elif not self.calibre and not self.telecode:
            raise ValidationError(_('CALIBRE or TELECODE ?'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        if self.calibre:
            calibre.file(self.xelon, self.comments, user)
        if self.telecode:
            telecode.file(self.xelon, self.comments, user)
        super().save(*args, **kwargs)

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
        if user and user.pk and not self.pk:
            self.created_by = user
        super().save(*args, **kwargs)

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
        super().save(*args, **kwargs)

    def __str__(self):
        first_name, last_name = self.created_by.first_name, self.created_by.last_name
        if first_name and last_name:
            return f"{self.created_by.last_name} {self.created_by.first_name} - {self.xelon_number}"
        else:
            return f"{self.created_by.username} - {self.xelon_number}"


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
    product = models.CharField('PRODUCT', max_length=200, blank=True)
    item = models.CharField('ITEM', max_length=200)
    time = models.CharField('TIME', max_length=10)
    info = models.TextField('INFO', max_length=2000)
    rmq = models.TextField('RMQ', max_length=2000, blank=True)
    action = models.TextField('ACTION/RETOUR', max_length=2000, blank=True)
    status = models.TextField('STATUT', max_length=50, default='En Attente', choices=STATUS_CHOICES)
    deadline = models.DateField('DATE LIMITE', null=True, blank=True)
    category = models.ForeignKey("SuptechCategory", on_delete=models.SET_NULL, null=True, blank=True)
    is_48h = models.BooleanField("Traitement 48h", default=False)
    to = models.TextField("TO", max_length=5000, default=conf.SUPTECH_TO_EMAIL_LIST)
    cc = models.TextField("CC", max_length=5000, default=conf.SUPTECH_CC_EMAIL_LIST)
    created_at = models.DateTimeField('ajouté le', editable=False, null=True)
    created_by = models.ForeignKey(User, related_name="suptechs_created", editable=False, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    modified_at = models.DateTimeField('modifié le', null=True)
    modified_by = models.ForeignKey(User, related_name="suptechs_modified", on_delete=models.SET_NULL, null=True,
                                    blank=True)
    messages = GenericRelation('Message')

    class Meta:
        verbose_name = "SupTech"
        ordering = ['pk']

    def to_list(self, category=None):
        cat_to_mails = SuptechCategory.get_to_mails(category)
        mailings = string_to_list(self.to)
        return list(OrderedDict.fromkeys(set(mailings + cat_to_mails)))

    def cc_list(self, category=None):
        cat_cc_mails = SuptechCategory.get_cc_mails(category)
        mailings = string_to_list(self.cc)
        return list(OrderedDict.fromkeys(set(mailings + cat_cc_mails)))

    def to_string(self, category=None):
        return "; ".join(self.to_list(category))

    def cc_string(self, category=None):
        return "; ".join(self.cc_list(category))

    def response_email(self, request):
        return self._send_email(request, is_action=True)

    def request_email(self, request):
        return self._send_email(request)

    def _send_email(self, request, is_action=False):
        if self.id:
            try:
                from_email = self.created_by.email
                to_list = string_to_list(self.to)
                cc_list = ([from_email] + string_to_list(self.cc))
                current_site = get_current_site(request)
                subject = f"[SUPTECH_{self.id}] {self.item}"
                if is_action:
                    from_email = self.modified_by.email
                    context = {"user": request.user, "suptech": self, 'domain': current_site.domain}
                    message = render_to_string('tools/email_format/suptech_response_email.html', context)
                    to_list = [self.created_by.email] + to_list
                    cc_list = ([from_email] + [email for email in list(set(cc_list)) if email != self.created_by.email])
                else:
                    context = {'email': from_email, 'suptech': self, 'domain': current_site.domain}
                    message = render_to_string('tools/email_format/suptech_request_email.html', context)
                files = self.suptechfile_set.filter(is_action=is_action)
                files = [f.file.path for f in files]
                send_email_task.delay(
                    subject=subject, body=message, from_email=from_email, to=to_list, cc=cc_list, files=files
                )
                return True
            except AttributeError:
                pass
        return False

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('tools:suptech_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.pk} - {self.item}"


class SuptechCategory(models.Model):
    name = models.CharField('nom', max_length=200)
    manager = models.ForeignKey(User, related_name="suptechs_manager", on_delete=models.SET_NULL, null=True, blank=True)
    to = models.TextField("TO", max_length=5000, default=conf.SUPTECH_TO_EMAIL_LIST, blank=True)
    cc = models.TextField("CC", max_length=5000, default=conf.SUPTECH_CC_EMAIL_LIST, blank=True)
    to_users = models.ManyToManyField(User, related_name="to_sup_cats", blank=True)
    cc_users = models.ManyToManyField(User, related_name="cc_sup_cats", blank=True)

    def to_list(self):
        to_emails = string_to_list(self.to)
        user_emails = list(self.to_users.values_list('email', flat=True).distinct())
        return list(OrderedDict.fromkeys(set(to_emails + user_emails)))

    def cc_list(self):
        cc_emails = string_to_list(self.cc)
        user_emails = list(self.cc_users.values_list('email', flat=True).distinct())
        return list(OrderedDict.fromkeys(set(cc_emails + user_emails)))

    def to_string(self):
        return "; ".join(self.to_list())

    def cc_string(self):
        return "; ".join(self.cc_list())

    @classmethod
    def get_mails(cls, pk):
        cats = cls.objects.filter(pk=pk)
        if cats:
            query = cats.first()
            return query.to_list(), query.cc_list()
        return [], []

    @classmethod
    def get_to_mails(cls, pk):
        return cls.get_mails(pk)[0]

    @classmethod
    def get_cc_mails(cls, pk):
        return cls.get_mails(pk)[1]

    def __str__(self):
        return self.name


class SuptechItem(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    extra = models.BooleanField(default=False)
    category = models.ForeignKey("SuptechCategory", on_delete=models.SET_NULL, null=True, blank=True)
    is_48h = models.BooleanField("Traitement 48h", default=True)
    is_active = models.BooleanField("Actif", default=True)
    mailing_list = models.TextField("Liste d'email", max_length=5000, default=conf.SUPTECH_TO_EMAIL_LIST, blank=True)
    cc_mailing_list = models.TextField("liste d'email CC", max_length=5000, default=conf.SUPTECH_CC_EMAIL_LIST, blank=True)
    to_users = models.ManyToManyField(User, related_name="to_sup_items", blank=True)
    cc_users = models.ManyToManyField(User, related_name="cc_sup_items", blank=True)

    class Meta:
        verbose_name = "SupTech Item"
        ordering = ['name']

    def to_list(self, category=None):
        cat_to_mails = self._get_cat_emails(category)[0]
        mailings = string_to_list(self.mailing_list)
        emails = list(self.to_users.values_list('email', flat=True).distinct())
        return list(OrderedDict.fromkeys(set(mailings + emails + cat_to_mails)))

    def cc_list(self, category=None):
        cat_cc_mails = self._get_cat_emails(category)[1]
        cc_mailings = string_to_list(self.cc_mailing_list)
        emails = list(self.cc_users.values_list('email', flat=True).distinct())
        return list(OrderedDict.fromkeys(set(cc_mailings + emails + cat_cc_mails)))

    def to_string(self, category=None):
        return "; ".join(self.to_list(category))

    def cc_string(self, category=None):
        return "; ".join(self.cc_list(category))

    def _get_cat_emails(self, category):
        cat_to_mails, cat_cc_mails = SuptechCategory.get_mails(category)
        if not cat_to_mails:
            cat_to_mails = self.category.to_list()
        if not cat_cc_mails:
            cat_cc_mails = self.category.cc_list()
        return cat_to_mails, cat_cc_mails

    def __str__(self):
        return self.name


class Infotech(models.Model):
    STATUS_CHOICES = [
        ('En Cours', 'En Cours'), ('Cloturée', 'Cloturée')
    ]

    item = models.CharField('ITEM', max_length=200)
    info = models.TextField('INFO', max_length=2000)
    action = models.TextField('ACTION/RETOUR', max_length=2000, blank=True)
    status = models.TextField('STATUT', max_length=50, default='En Cours', choices=STATUS_CHOICES)
    to = models.TextField("TO", max_length=5000)
    cc = models.TextField("CC", max_length=5000)
    created_at = models.DateTimeField('ajouté le', auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="infotechs_created", editable=False, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    modified_at = models.DateTimeField('modifié le', null=True)
    modified_by = models.ForeignKey(User, related_name="infotechs_modified", on_delete=models.SET_NULL, null=True,
                                    blank=True)
    messages = GenericRelation('Message')

    class Meta:
        verbose_name = "InfoTech"
        ordering = ['pk']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('tools:infotech_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.pk} - {self.item}"


class InfotechMailingList(models.Model):
    name = models.CharField('Nom', max_length=100, unique=True)
    is_active = models.BooleanField("Actif", default=True)
    to_users = models.ManyToManyField(User, related_name="to_info_emails", blank=True)
    cc_users = models.ManyToManyField(User, related_name="cc_info_emails", blank=True)

    class Meta:
        verbose_name = "InfoTech Mailing List"
        ordering = ['name']

    def to_list(self):
        emails = list(self.to_users.values_list('email', flat=True).distinct())
        if emails and isinstance(emails, list):
            return "; ".join(emails)
        return ""

    def cc_list(self):
        emails = list(self.cc_users.values_list('email', flat=True).distinct())
        if emails and isinstance(emails, list):
            return "; ".join(emails)
        return ""

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.TextField()
    added_at = models.DateTimeField('ajouté le', null=True, blank=True)
    added_by = models.ForeignKey(User, related_name="message_added", on_delete=models.SET_NULL, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "SupTech Message"
        ordering = ['-added_at']

    def __str__(self):
        return f"Message de {self.added_by} sur {self.content_object}"

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.added_by and user and user.pk:
            self.added_by = user
        if not self.added_at:
            self.added_at = timezone.now()
        super().save(*args, **kwargs)


class SuptechFile(models.Model):
    file = models.FileField(upload_to="suptech/%Y/%m")
    is_action = models.BooleanField("action", default=False)
    suptech = models.ForeignKey("Suptech", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Suptech File"

    def __str__(self):
        return f"[SUPTECH_{self.suptech.pk}] {self.file.name}"


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


class RaspiTime(models.Model):
    TYPE_CHOICES = [('RASPEEDI', 'RASPEEDI'), ('AET', 'AET'), ('CANPI', 'CANPI')]

    name = models.CharField('Nom de la machine', max_length=100)
    type = models.CharField('type', max_length=50, choices=TYPE_CHOICES)
    date = models.DateField('date', auto_now_add=True)
    start_time = models.TimeField('heure de START', auto_now_add=True)
    end_time = models.TimeField('heure de FIN', null=True, blank=True)
    duration = models.IntegerField('durée en secondes', null=True, blank=True)
    xelon = models.CharField('n° Xelon', max_length=10, blank=True)

    class Meta:
        verbose_name = ("RasPi Time")
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


class ConfigFile(models.Model):
    name = models.CharField("nom du logiciel", max_length=100, unique=True)
    path = models.CharField("chemin du fichier", max_length=500, unique=True)
    filename = models.CharField("nom du fichier", max_length=100)
    content = models.TextField("contenu du fichier")

    def __str__(self):
        return self.name
