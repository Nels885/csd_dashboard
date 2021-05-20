from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from crum import get_current_user


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
    nom_technicien = models.CharField('nom technicien', max_length=50, blank=True)
    commentaire_sav_admin = models.CharField('commentaire SAV Admin', max_length=5000, blank=True)
    commentaire_de_la_fr = models.CharField('commentaire de la FR', max_length=5000, blank=True)
    commentaire_action = models.CharField('commentaire action', max_length=5000, blank=True)
    libelle_de_la_fiche_cas = models.CharField('libellé de la fiche cas', max_length=5000, blank=True)
    dossier_vip = models.BooleanField('dossier VIP', default=False)
    express = models.BooleanField('express', default=False)
    ilot = models.CharField('ilot', max_length=100, blank=True)
    vin_error = models.BooleanField('Erreur VIN', default=False)
    is_active = models.BooleanField('Actif', default=False)
    corvet = models.ForeignKey('psa.Corvet', on_delete=models.SET_NULL, null=True, blank=True)
    actions = GenericRelation('Action')

    class Meta:
        verbose_name = "dossier Xelon"
        ordering = ['numero_de_dossier']
        permissions = [
            ("change_product", "Can change product"), ("email_product", "Can send email product"),
            ("change_vin", "Can change vin"), ("email_vin", "Can send email vin"),
            ("active_xelon", "Can active xelon")
        ]

    def save(self, *args, **kwargs):
        from psa.models import Corvet
        try:
            self.corvet = Corvet.objects.get(pk=self.vin)
            self.vin_error = False
        except ObjectDoesNotExist:
            pass
        super(Xelon, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.numero_de_dossier, self.vin, self.modele_produit, self.modele_vehicule)


class ProductCode(models.Model):
    name = models.CharField('code Produit', max_length=100)

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

    product_model = models.CharField('modèle produit', max_length=50, unique=True)
    category = models.CharField('catégorie', max_length=50, choices=CHOICES, blank=True)

    class Meta:
        verbose_name = "Catégorie Produit"
        ordering = ['product_model']

    def __str__(self):
        return self.product_model
