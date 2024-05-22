import re

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from crum import get_current_user

from utils.regex import REF_PSA_REGEX

from psa.models import Corvet, Multimedia, Ecu, CORVET_HW_FILTERS, CORVET_SN_FILTERS
from psa.choices import ECU_TYPE_CHOICES, BTEL_TYPE_CHOICES


XELON_FILTERS = [
    'numero_de_dossier__iexact', 'vin__iexact', 'vin__iendswith', 'corvet__opts__tag__istartswith'
]
XELON_SN_FILTERS = [f'corvet__{field}' for field in CORVET_SN_FILTERS]
XELON_HW_FILTERS = [f'corvet__{field}' for field in CORVET_HW_FILTERS]


class Xelon(models.Model):
    numero_de_dossier = models.CharField('numéro de dossier', max_length=10, unique=True)
    vin = models.CharField('V.I.N.', max_length=17, blank=True)
    modele_produit = models.CharField('modèle produit', max_length=50, blank=True)
    modele_vehicule = models.CharField('modèle véhicule', max_length=50, blank=True)
    famille_client = models.CharField('famille Client', max_length=5000, blank=True)
    famille_produit = models.CharField('famille produit', max_length=100, blank=True)
    date_retour = models.DateField('date retour', null=True, blank=True)
    delai_au_en_jours_ouvres = models.IntegerField('délai en jours ouvrés', null=True, blank=True)
    delai_au_en_jours_calendaires = models.IntegerField('délai en jours calendaires', null=True, blank=True)
    date_de_cloture = models.DateTimeField('date de clôture', null=True, blank=True)
    type_de_cloture = models.CharField('type de clôture', max_length=50, blank=True)
    lieu_de_stockage = models.CharField('lieu de stockage', max_length=50, blank=True)
    code_magasin = models.CharField('Code Magasin', max_length=50, blank=True)
    code_zone = models.CharField('Code Zone', max_length=50, blank=True)
    nom_technicien = models.CharField('nom technicien', max_length=50, blank=True)
    commentaire_sav_admin = models.CharField('commentaire SAV Admin', max_length=5000, blank=True)
    commentaire_de_la_fr = models.CharField('commentaire de la FR', max_length=5000, blank=True)
    commentaire_action = models.CharField('commentaire action', max_length=5000, blank=True)
    libelle_de_la_fiche_cas = models.CharField('libellé de la fiche cas', max_length=5000, blank=True)
    dossier_vip = models.BooleanField('dossier VIP', default=False)
    express = models.BooleanField('express', default=False)
    ilot = models.CharField('ilot', max_length=100, blank=True)
    date_expedition_attendue = models.DateField('date expédition attendue', null=True, blank=True)
    delai_expedition_attendue = models.IntegerField('délai expédition attendue', null=True, blank=True)
    rm = models.CharField('RM', max_length=50, blank=True)
    pays = models.CharField('Pays', max_length=100, blank=True)
    telecodage = models.CharField('TELECODAGE', max_length=50, blank=True)
    appairage = models.CharField('APPAIRAGE', max_length=50, blank=True)
    vin_error = models.BooleanField('Erreur VIN', default=False)
    is_active = models.BooleanField('Actif', default=False)
    corvet = models.ForeignKey('psa.Corvet', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('squalaetp.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True)
    actions = GenericRelation('Action')

    class Meta:
        verbose_name = "dossier Xelon"
        ordering = ['numero_de_dossier']
        permissions = [
            ("change_product", "Can change product"), ("email_product", "Can send email product"),
            ("change_vin", "Can change vin"), ("email_vin", "Can send email vin"),
            ("email_admin", "Can send email admin"), ("active_xelon", "Can active xelon")
        ]

    @staticmethod
    def prod_search(value):
        if value and re.match(REF_PSA_REGEX, value):
            parts = ProductCode.objects.filter(name__icontains=value)
            if not value[-2:].isdigit():
                value = value[:-2] + '77'
            media = Multimedia.objects.filter(Q(comp_ref__exact=value) | Q(label_ref__exact=value)).first()
            prod = Ecu.objects.filter(Q(comp_ref__exact=value) | Q(label_ref__exact=value)).first()
            vehicles = Corvet.get_vehicles(value)
            return parts, media, prod, vehicles
        return tuple(None for _ in range(4))

    @classmethod
    def search(cls, value):
        if value is not None:
            value = value.strip()
            if re.match(REF_PSA_REGEX, str(value)) and not value[-2:].isdigit():
                value = value[:-2] + '77'
            filters = XELON_FILTERS + XELON_SN_FILTERS + XELON_HW_FILTERS
            for field in filters:
                    queryset = cls.objects.filter(**{field: value})
                    if queryset: return queryset
        return None

    @property
    def option(self):
        if self.telecodage == "1":
            return "TELE"
        elif self.appairage == "1":
            return "APPAIR"
        return ""

    def __str__(self):
        return "{} - {} - {} - {}".format(self.numero_de_dossier, self.vin, self.modele_produit, self.modele_vehicule)


def get_deadline():
    return timezone.now() + timezone.timedelta(days=7)


class XelonTemporary(models.Model):
    numero_de_dossier = models.CharField('numéro de dossier', max_length=10)
    vin = models.CharField('V.I.N.', max_length=17)
    modele_produit = models.CharField('modèle produit', max_length=50, blank=True)
    modele_vehicule = models.CharField('modèle véhicule', max_length=50, blank=True)
    is_active = models.BooleanField('Actif', default=False)
    end_date = models.DateField('date de fin', default=get_deadline, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    corvet = models.ForeignKey('psa.Corvet', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        try:
            Xelon.objects.get(numero_de_dossier=self.numero_de_dossier)
            raise ValidationError(_('Xelon number exists !'))
        except Xelon.DoesNotExist:
            for query in XelonTemporary.objects.filter(numero_de_dossier=self.numero_de_dossier):
                if self.is_active and query.is_active:
                    raise ValidationError(_('A temporary Xelon is already active with this number !'))

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.numero_de_dossier, self.vin, self.modele_produit, self.modele_vehicule)


class ProductCode(models.Model):
    name = models.CharField('code Produit', max_length=100)
    medias = models.ManyToManyField('psa.Multimedia', related_name='parts', blank=True)
    ecus = models.ManyToManyField('psa.Ecu', related_name='parts', blank=True)

    def __str__(self):
        return self.name


class SparePart(models.Model):
    code_magasin = models.CharField('code Magasin', max_length=50, blank=True)
    code_zone = models.CharField('code Zone', max_length=50, blank=True)
    code_site = models.IntegerField('code Site', null=True, blank=True)
    code_emplacement = models.CharField('code Emplacement', max_length=50, blank=True)
    cumul_dispo = models.IntegerField('cumul Dispo', null=True, blank=True)
    code_produit = models.ForeignKey('ProductCode', on_delete=models.CASCADE)


class Indicator(models.Model):
    date = models.DateField('Date du jours', unique=True)
    products_to_repair = models.IntegerField('Produits à réparer')
    late_products = models.IntegerField('Produits en retard')
    express_products = models.IntegerField('Produits express')
    output_products = models.IntegerField('Produits en sortie')
    xelons = models.ManyToManyField('Xelon')

    @classmethod
    def count_prods(cls):
        query = cls.objects.order_by("-date").first()
        if query:
            prod_list = ["RT6", "SMEG", "NAC", "RNEG", "NG4", "DISPLAY", "NISSAN", "BSI", "BSM"]
            data = {key: query.xelons.filter(modele_produit__startswith=key).count() for key in prod_list}
            data['RTx'] = query.xelons.filter(modele_produit__in=['RT3', 'RT4', 'RT5']).count()
            data['CALC_MOT'] = query.xelons.filter(famille_produit__exact="CALC MOT").count()
            data['AUTOTRONIK'] = Xelon.objects.filter(lieu_de_stockage="ATELIER/AUTOTRONIK").exclude(
                type_de_cloture__in=['Réparé', 'Admin', 'N/A']).count()
            data['AUTRES'] = query.xelons.all().count() - sum(data.values())
        else:
            data = {}
        return data

    def __str__(self):
        return str(self.date)


class Action(models.Model):
    content = models.TextField()
    modified_at = models.DateTimeField('modifié le', auto_now=True)
    modified_by = models.ForeignKey(User, related_name="action_modified", on_delete=models.SET_NULL, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Modification"
        ordering = ['-modified_at']

    def __str__(self):
        return "Action de {} sur {}".format(self.modified_by, self.content_object)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.pk:
            self.modified_by = user
        super(Action, self).save(*args, **kwargs)


class ProductCategory(models.Model):
    CHOICES = [
        ('PSA', 'Produits PSA'), ('AUTRE', 'Autres produits'), ('CLARION', 'Clarion'), ('ETUDE', 'Etude'),
        ('CALCULATEUR', 'Calculateurs'), ('DEFAUT', 'Defaut')
    ]
    TYPES = BTEL_TYPE_CHOICES + ECU_TYPE_CHOICES

    product_model = models.CharField('modèle produit', max_length=50, unique=True)
    category = models.CharField('catégorie', default="DEFAUT", max_length=50, choices=CHOICES)
    corvet_type = models.CharField('Type Corvet', max_length=50, choices=TYPES, blank=True)
    animator = models.ForeignKey(User, related_name="animator_prods", on_delete=models.SET_NULL, null=True)
    niv_t_users = models.ManyToManyField(User, related_name='niv_t_prods', blank=True)
    niv_i_users = models.ManyToManyField(User, related_name='niv_i_prods', blank=True)
    niv_l_users = models.ManyToManyField(User, related_name='niv_l_prods', blank=True)
    niv_u_users = models.ManyToManyField(User, related_name='niv_u_prods', blank=True)
    niv_o_users = models.ManyToManyField(User, related_name='niv_o_prods', blank=True)
    fa_users = models.ManyToManyField(User, related_name='fa_prods', blank=True)
    fe_users = models.ManyToManyField(User, related_name='fe_prods', blank=True)

    class Meta:
        verbose_name = "Catégorie Produit"
        ordering = ['product_model']

    def __str__(self):
        return self.product_model


class Sivin(models.Model):
    immat_siv = models.CharField('Immatriculation SIV', max_length=20, primary_key=True)
    codif_vin = models.CharField('V.I.N.', max_length=17)
    type_vin_cg = models.CharField('Type VIN C.G. (VDS)', max_length=6, blank=True)
    type_var_vers_prf = models.CharField('Type var vers prf', max_length=100, blank=True)
    n_serie = models.CharField('Numéro de série (VIS)', max_length=8, blank=True)
    n_siren = models.CharField('Numéro Siren', max_length=100, blank=True)
    date_1er_cir = models.CharField('Date 1ère circulation', max_length=100, blank=True)
    date_dcg = models.CharField('Date C.G.', max_length=100, blank=True)
    marque = models.CharField('Marque', max_length=100, blank=True)
    marque_carros = models.CharField('Marque carrosserie', max_length=100, blank=True)
    modele = models.CharField('Modèle', max_length=100, blank=True)
    modele_etude = models.CharField('Modèle étude', max_length=100, blank=True)
    modele_prf = models.CharField('Modèle préférence', max_length=100, blank=True)
    genre_v = models.CharField('Genre véhicule', max_length=100, blank=True)
    genre_vcg = models.CharField('Genre véhicule C.G.', max_length=100, blank=True)
    nb_portes = models.CharField('Nombre portes', max_length=100, blank=True)
    nb_pl_ass = models.CharField('Nombre de places assises', max_length=100, blank=True)
    version = models.CharField('Version', max_length=100, blank=True)
    energie = models.CharField('Energie', max_length=100, blank=True)
    puis_ch = models.CharField('Puissance chevau', max_length=100, blank=True)
    puis_fisc = models.CharField('Puissance fiscale', max_length=100, blank=True)
    puis_kw = models.CharField('Puissance Kw', max_length=100, blank=True)
    cons_exurb = models.CharField('Consommation hors agglomération', max_length=100, blank=True)
    cons_mixte = models.CharField('Consommation mixte', max_length=100, blank=True)
    cons_urb = models.CharField('Consommation agglomération', max_length=100, blank=True)
    carrosserie = models.CharField('Carrosserie', max_length=100, blank=True)
    carrosserie_cg = models.CharField('Carrosserie C.G.', max_length=100, blank=True)
    couleur_vehic = models.CharField('Couleur véhicule', max_length=100, blank=True)
    empat = models.CharField('Empattement véhicule', max_length=100, blank=True)
    hauteur = models.CharField('Hauteur', max_length=100, blank=True)
    largeur = models.CharField('Largeur', max_length=100, blank=True)
    longueur = models.CharField('Longueur', max_length=100, blank=True)
    latitude = models.CharField('Latitude', max_length=100, blank=True)
    poids_vide = models.CharField('Poids à vide', max_length=100, blank=True)
    ptr = models.CharField('PTR', max_length=100, blank=True)
    ptr_prf = models.CharField('PTR Prf', max_length=100, blank=True)
    pneus = models.CharField('Pneus', max_length=100, blank=True)
    code_moteur = models.CharField('Code moteur', max_length=100, blank=True)
    mode_inject = models.CharField("Mode d'injection", max_length=100, blank=True)
    cylindree = models.CharField('Cylindrée', max_length=100, blank=True)
    nb_cylind = models.CharField('Nombre cylindres', max_length=100, blank=True)
    nb_soupape = models.CharField('Nombre soupapes', max_length=100, blank=True)
    turbo_compr = models.CharField('Turbo compresseur', max_length=100, blank=True)
    co2 = models.CharField('Emission CO2', max_length=100, blank=True)
    depollution = models.CharField('Dépollution', max_length=100, blank=True)
    tp_boit_vit = models.CharField('Type de boîte de vitesse', max_length=100, blank=True)
    nb_vitesse = models.CharField('Nombre de vitesses', max_length=100, blank=True)
    nb_volume = models.CharField('Nombre de volume', max_length=100, blank=True)
    propulsion = models.CharField('Type propulsion', max_length=100, blank=True)
    type = models.CharField('Type', max_length=100, blank=True)
    prix_vehic = models.CharField('Prix véhicule', max_length=100, blank=True)
    corvet = models.OneToOneField(Corvet, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Données SIVIN"
        ordering = ['immat_siv']

    @classmethod
    def search(cls, value):
        if value is not None:
            query = re.sub(r'[ -]', '', value.strip())
            return cls.objects.filter(immat_siv__iexact=query)
        return None

    def __str__(self):
        return f"{self.immat_siv} - {self.codif_vin}"
