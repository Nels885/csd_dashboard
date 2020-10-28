from django.db import models


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

    class Meta:
        verbose_name = "dossier Xelon"
        ordering = ['numero_de_dossier']

    def __str__(self):
        return "{} - {} - {} - {}".format(self.numero_de_dossier, self.vin, self.modele_produit, self.modele_vehicule)


class CorvetBackup(models.Model):
    vin = models.CharField('V.I.N.', max_length=17, unique=True)
    data = models.CharField('liste des données Corvet', max_length=5000)

    def __str__(self):
        return self.vin


class Corvet(models.Model):
    vin = models.CharField('V.I.N.', max_length=17, primary_key=True)
    donnee_date_debut_garantie = models.DateTimeField('Date d?but garantie', null=True, blank=True)
    donnee_date_entree_montage = models.DateTimeField('Date entr?e montage', null=True, blank=True)
    donnee_ligne_de_produit = models.CharField('LIGNE_DE_PRODUIT', max_length=200, blank=True)
    donnee_marque_commerciale = models.CharField('MARQUE_COMMERCIALE', max_length=200, blank=True)
    donnee_silhouette = models.CharField('SILHOUETTE', max_length=200, blank=True)
    donnee_genre_de_produit = models.CharField('GENRE_DE_PRODUIT', max_length=200, blank=True)
    attribut_ddo = models.CharField('KIT TELEPHONE MAIN LIBRE', max_length=200, blank=True)
    attribut_dgm = models.CharField('COMBINE (CARACTERISTIQUES)', max_length=200, blank=True)
    attribut_dhb = models.CharField('HAUT PARLEUR', max_length=200, blank=True)
    attribut_dhg = models.CharField('COMMANDE AUTO-RADIO', max_length=200, blank=True)
    attribut_djq = models.CharField('COMPACT DISQUE', max_length=200, blank=True)
    attribut_djy = models.CharField('SYSTEME NAVIGATION', max_length=200, blank=True)
    attribut_dkx = models.CharField('CARTOGRAPHIE POUR NAVIGATION', max_length=200, blank=True)
    attribut_dlx = models.CharField('AFFICHEUR AV', max_length=200, blank=True)
    attribut_doi = models.CharField('RECEPTION RADIO AMELIOREE', max_length=200, blank=True)
    attribut_dqm = models.CharField('TYPAGE GMP', max_length=200, blank=True)
    attribut_dqs = models.CharField('WIFI', max_length=200, blank=True)
    attribut_drc = models.CharField('RECEPTEUR RADIO', max_length=200, blank=True)
    attribut_drt = models.CharField('REGULATION CLIMAT/TEMPERATURE', max_length=200, blank=True)
    attribut_dti = models.CharField('TUNER RADIO', max_length=200, blank=True)
    attribut_dun = models.CharField('AMPLI EQUALISEUR', max_length=200, blank=True)
    attribut_dwl = models.CharField('PACK RADIO/INFO/COMMUNICATION', max_length=200, blank=True)
    attribut_dwt = models.CharField('PACK PREEQUIP. RADIO/COMMUNIC.', max_length=200, blank=True)
    attribut_dxj = models.CharField('ECRAN VIDEO AR', max_length=200, blank=True)
    attribut_dyb = models.CharField('VISION TETE HAUTE', max_length=200, blank=True)
    attribut_dym = models.CharField('PRISE AUXILIAIRE PACK AUDIO', max_length=200, blank=True)
    attribut_dyr = models.CharField('BOITIER TELEMATIQUE', max_length=200, blank=True)
    attribut_dzv = models.CharField('AIDE A LA CONDUITE', max_length=200, blank=True)
    attribut_gg8 = models.CharField('PAYS PROGRAMME (ICP)', max_length=200, blank=True)
    electronique_14f = models.CharField('RADIO HARD - Recepteur Radio', max_length=200, blank=True)
    electronique_14j = models.CharField('CLIM HARD - Climatisation', max_length=200, blank=True)
    electronique_14k = models.CharField('CMB HARD - Combine Planche de Bord', max_length=200, blank=True)
    electronique_14l = models.CharField('EMF HARD - Ecran Multifonctions', max_length=200, blank=True)
    electronique_14r = models.CharField('AAS HARD - Aide Au Stationnement', max_length=200, blank=True)
    electronique_14x = models.CharField('BTEL HARD - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_19z = models.CharField('FMUX_HARD - FAÇADE MULTIPLEXÉ', max_length=200, blank=True)
    electronique_44f = models.CharField('RADIO FOURN.NO.SERIE - Recepteur Radio', max_length=200, blank=True)
    electronique_44l = models.CharField('EMF FOURN.NO.SERIE - Ecran Multifonctions', max_length=200, blank=True)
    electronique_44x = models.CharField('BTEL FOURN.NO.SERIE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_54f = models.CharField('RADIO FOURN.DATE.FAB - Recepteur Radio', max_length=200, blank=True)
    electronique_54k = models.CharField('CMB FOURN.DATE.FAB - Combine Planche de Bord', max_length=200, blank=True)
    electronique_54l = models.CharField('EMF FOURN.DATE.FAB - Ecran Multifonctions', max_length=200, blank=True)
    electronique_84f = models.CharField('RADIO DOTE - Recepteur Radio', max_length=200, blank=True)
    electronique_84l = models.CharField('EMF DOTE - Ecran Multifonctions', max_length=200, blank=True)
    electronique_84x = models.CharField('BTEL DOTE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_94f = models.CharField('RADIO SOFT - Recepteur Radio', max_length=200, blank=True)
    electronique_94l = models.CharField('EMF SOFT - Ecran Multifonctions', max_length=200, blank=True)
    electronique_94x = models.CharField('BTEL SOFT - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    attribut_dat = models.CharField('ANTENNE', max_length=200, blank=True)
    attribut_dcx = models.CharField('COTE  CONDUITE/POSTE CONDUITE', max_length=200, blank=True)
    electronique_19h = models.CharField('MDS HARD - Module de service telematique', max_length=200, blank=True)
    electronique_49h = models.CharField('MDS FOURN.NO.SERIE - Module de service telematique', max_length=200, blank=True)
    electronique_64f = models.CharField('RADIO FOURN.CODE - Recepteur Radio', max_length=200, blank=True)
    electronique_64x = models.CharField('BTEL FOURN.CODE - Boitier Telematique (radio telephone)', max_length=200, blank=True)
    electronique_69h = models.CharField('MDS FOURN.CODE - Module de service telematique', max_length=200, blank=True)
    electronique_89h = models.CharField('MDS DOTE - Module de service telematique', max_length=200, blank=True)
    electronique_99h = models.CharField('MDS SOFT - Module de service telematique', max_length=200, blank=True)
    electronique_14a = models.CharField('CMM HARD - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_34a = models.CharField('CMM SOFT LIVRE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_44a = models.CharField('CMM FOURN.NO.SERIE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_54a = models.CharField('CMM FOURN.DATE.FAB - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_64a = models.CharField('CMM FOURN.CODE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_84a = models.CharField('CMM DOTE - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_94a = models.CharField('CMM SOFT - Calculateur Moteur Multifonction', max_length=200, blank=True)
    electronique_p4a = models.CharField('CMM EOBD - Calculateur Moteur Multifonction', max_length=200, blank=True)
    donnee_moteur = models.CharField('MOTEUR', max_length=200, blank=True)
    donnee_transmission = models.CharField('TRANSMISSION', max_length=200, blank=True)
    organes_10 = models.CharField('MOTEUR', max_length=200, blank=True)
    electronique_14b = models.CharField('BSI HARD - Boitier Servitude Intelligent', max_length=200, blank=True)
    organes_20 = models.CharField('BOITE DE VITESSES', max_length=200, blank=True)
    electronique_44b = models.CharField('BSI FOURN.NO.SERIE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_54b = models.CharField('BSI FOURN.DATE.FAB - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_64b = models.CharField('BSI FOURN.CODE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_84b = models.CharField('BSI DOTE - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_94b = models.CharField('BSI SOFT - Boitier Servitude Intelligent', max_length=200, blank=True)
    electronique_16p = models.CharField('HDC HARD - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_46p = models.CharField('HDC FOURN.NO.SERIE - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_56p = models.CharField('HDC FOURN.DATE.FAB - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_66p = models.CharField('HDC FOURN.CODE - Haut de Colonne de Direction (COM200x)', max_length=200, blank=True)
    electronique_16b = models.CharField('BSM HARD - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_46b = models.CharField('BSM FOURN.NO.SERIE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_56b = models.CharField('BSM FOURN.DATE.FAB - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_66b = models.CharField('BSM FOURN.CODE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_86b = models.CharField('BSM DOTE - Boitier Servitude Moteur', max_length=200, blank=True)
    electronique_96b = models.CharField('BSM SOFT - Boitier Servitude Moteur', max_length=200, blank=True)
    xelons = models.ManyToManyField(Xelon, related_name='corvet', blank=True)

    class Meta:
        verbose_name = "données CORVET"
        ordering = ['vin']

    def __str__(self):
        return self.vin


class ProductCode(models.Model):
    name = models.CharField('code Produit', max_length=100)

    def __str__(self):
        return self.name


class Stock(models.Model):
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

    def count_prods(self):
        prod_list = ["RT6", "SMEG", "NAC", "RNEG", "NG4", "DISPLAY", "NISSAN", "BSI", "BSM"]
        data = {key: self.xelons.filter(modele_produit__startswith=key).count() for key in prod_list}
        data['RTx'] = self.xelons.filter(modele_produit__in=['RT3', 'RT4', 'RT5']).count()
        data['CALC_MOT'] = self.xelons.filter(famille_produit__exact="CALC MOT").count()
        data['AUTRES'] = self.xelons.all().count() - sum(data.values())
        return data

    def __str__(self):
        return str(self.date)
