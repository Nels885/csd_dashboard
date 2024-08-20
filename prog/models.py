from urllib.parse import urljoin
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from squalaetp.models import Xelon
from dashboard.models import UserProfile, User


class Raspeedi(models.Model):

    TYPE_CHOICES = [('RAD', 'Radio'), ('NAV', 'Navigation')]
    CON_CHOICES = [(1, '1'), (2, '2')]
    MEDIA_CHOICES = [
        ('N/A', 'Vide'),
        ('HDD', 'Disque Dur'),
        ('8Go', 'Carte SD 8Go'),
        ('16Go', 'Carte SD 16Go'),
        ('8Go 16Go', 'Carte SD 8 ou 16 Go'),
    ]
    PRODUCT_CHOICES = [
        ('RT4', 'RT4'),
        ('RT5', 'RT5'),
        ('RT6', 'RT6'),
        ('RT6v2', 'RT6 version 2'),
        ('SMEG', 'SMEG'),
        ('SMEGP', 'SMEG+ / SMEG+ IV1'),
        ('SMEGP2', 'SMEG+ IV2'),
    ]

    ref_boitier = models.BigIntegerField('référence boîtier', primary_key=True)
    produit = models.CharField('produit', max_length=20, choices=PRODUCT_CHOICES)
    facade = models.CharField('façade', max_length=2)
    type = models.CharField('type', max_length=3, choices=TYPE_CHOICES)
    dab = models.BooleanField('DAB', default=False)
    cam = models.BooleanField('caméra de recul', default=False)
    dump_peedi = models.CharField('dump PEEDI', max_length=25, blank=True)
    cd_version = models.CharField('version CD', max_length=10, blank=True)
    media = models.CharField('type de média', max_length=20, choices=MEDIA_CHOICES, blank=True)
    carto = models.CharField('version cartographie', max_length=20, blank=True)
    dump_renesas = models.CharField('dump RENESAS', max_length=50, blank=True)
    ref_mm = models.CharField('référence MM', max_length=200, blank=True)
    connecteur_ecran = models.IntegerField("nombre de connecteur d'écran", choices=CON_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Données RASPEEDI"
        ordering = ['ref_boitier']

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.ref_boitier, self.produit, self.facade, self.type)


class Programing(models.Model):
    psa_barcode = models.BigIntegerField('référence boîtier', primary_key=True)
    peedi_path = models.CharField('dossier PEEDI', max_length=20)
    peedi_dump = models.CharField('dump PEEDI', max_length=25, blank=True)
    renesas_dump = models.CharField('dump RENESAS', max_length=50, blank=True)
    multimedia = models.OneToOneField('psa.Multimedia', related_name='prog', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Données Programmation"
        ordering = ['psa_barcode']

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return str(self.psa_barcode)


class AddReference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    add_product = models.ForeignKey(Raspeedi, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UnlockProduct(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    unlock = models.ForeignKey(Xelon, editable=False, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField('ajouté le', editable=False, auto_now_add=True)
    modified_at = models.DateTimeField('modifié le', auto_now=True)

    class Meta:
        verbose_name = "Déverrouillage VIN"
        ordering = ['-created_at']

    def __str__(self):
        return self.unlock.numero_de_dossier


class ToolStatus(models.Model):
    name = models.CharField("Nom de l'outils", max_length=50)
    url = models.CharField("Lien web", max_length=500, blank=True)
    type = models.TextField("Type", max_length=50, blank=True)
    comment = models.TextField("Commentaire", blank=True)
    status_path = models.CharField("Chemin page statut", max_length=500, blank=True)
    api_path = models.CharField("Chemin API", max_length=500, blank=True)
    last_boot = models.DateTimeField("Dernier démarrage", null=True, blank=True)
    firmware = models.CharField("Firmware", max_length=20, blank=True)
    hostname = models.CharField("Hostname", max_length=50, blank=True)
    ip_addr = models.CharField("ip address", max_length=50, blank=True)
    mac_addr = models.CharField("mac address", max_length=20, blank=True)
    hw_revision = models.CharField('Hardware revision', max_length=500, blank=True)
    mbed_list = models.TextField("Liste mbed de l'AET", max_length=500, blank=True)
    logs = GenericRelation('Log')

    class Meta:
        verbose_name = "Statut Outil"
        ordering = ['name']
        permissions = [("view_info_tools", "Can view info tools")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self, 'status_url', self.get_url('status'))
        setattr(self, 'api_url', self.get_url('api'))

    def get_url(self, mode):
        url = self.url
        if not url and self.ip_addr:
            url = f"http://{self.ip_addr}/"
        if mode and mode == 'restart':
            return urljoin(url, "api/restart/")
        elif mode and mode == 'stop':
            return urljoin(url, "api/stop/")
        elif mode and mode == "api":
            return urljoin(url, self.api_path)
        elif mode and mode == 'status':
            return urljoin(url, self.status_path)
        return ""

    def __str__(self):
        return f"{self.name} - {self.url}"


class Log(models.Model):
    content = models.TextField()
    added_at = models.DateTimeField('ajouté le', editable=False, auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Log"
        ordering = ['-added_at']

    def __str__(self):
        return self.content_object


class AET(models.Model):
    name = models.CharField("Nom de l'AET", max_length=100, unique=True)
    raspi_url = models.CharField("URL Raspi", max_length=500)
    mbed_list = models.TextField("Liste mbed de l'AET", max_length=500, blank=True)

    class Meta:
        verbose_name = "Statut AET"
        ordering = ['name']

    def __str__(self):
        return self.name


class MbedFirmware(models.Model):
    name = models.CharField("Nom du soft mbed", max_length=100, unique=True)
    version = models.CharField("Version du soft", max_length=10, validators=[RegexValidator(r'[0-9]{1,2}.[0-9]{2}$', "Please respect version format (ex : 1.23)")])
    modified_at = models.DateTimeField('Modifié le', auto_now=True)
    filepath = models.FileField(upload_to='firmware/')

    def __str__(self):
        return self.name
