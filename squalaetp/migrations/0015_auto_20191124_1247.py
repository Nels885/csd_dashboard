# Generated by Django 2.2.7 on 2019-11-24 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squalaetp', '0014_auto_20191114_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dat',
            field=models.CharField(blank=True, max_length=200, verbose_name='ANTENNE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dcx',
            field=models.CharField(blank=True, max_length=200, verbose_name='COTE  CONDUITE/POSTE CONDUITE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_ddo',
            field=models.CharField(blank=True, max_length=200, verbose_name='KIT TELEPHONE MAIN LIBRE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dgm',
            field=models.CharField(blank=True, max_length=200, verbose_name='COMBINE (CARACTERISTIQUES)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dhb',
            field=models.CharField(blank=True, max_length=200, verbose_name='HAUT PARLEUR'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dhg',
            field=models.CharField(blank=True, max_length=200, verbose_name='COMMANDE AUTO-RADIO'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_djq',
            field=models.CharField(blank=True, max_length=200, verbose_name='COMPACT DISQUE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_djy',
            field=models.CharField(blank=True, max_length=200, verbose_name='SYSTEME NAVIGATION'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dkx',
            field=models.CharField(blank=True, max_length=200, verbose_name='CARTOGRAPHIE POUR NAVIGATION'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dlx',
            field=models.CharField(blank=True, max_length=200, verbose_name='AFFICHEUR AV'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_doi',
            field=models.CharField(blank=True, max_length=200, verbose_name='RECEPTION RADIO AMELIOREE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dqm',
            field=models.CharField(blank=True, max_length=200, verbose_name='TYPAGE GMP'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dqs',
            field=models.CharField(blank=True, max_length=200, verbose_name='WIFI'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_drc',
            field=models.CharField(blank=True, max_length=200, verbose_name='RECEPTEUR RADIO'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_drt',
            field=models.CharField(blank=True, max_length=200, verbose_name='REGULATION CLIMAT/TEMPERATURE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dti',
            field=models.CharField(blank=True, max_length=200, verbose_name='TUNER RADIO'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dun',
            field=models.CharField(blank=True, max_length=200, verbose_name='AMPLI EQUALISEUR'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dwl',
            field=models.CharField(blank=True, max_length=200, verbose_name='PACK RADIO/INFO/COMMUNICATION'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dwt',
            field=models.CharField(blank=True, max_length=200, verbose_name='PACK PREEQUIP. RADIO/COMMUNIC.'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dxj',
            field=models.CharField(blank=True, max_length=200, verbose_name='ECRAN VIDEO AR'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dyb',
            field=models.CharField(blank=True, max_length=200, verbose_name='VISION TETE HAUTE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dym',
            field=models.CharField(blank=True, max_length=200, verbose_name='PRISE AUXILIAIRE PACK AUDIO'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dyr',
            field=models.CharField(blank=True, max_length=200, verbose_name='BOITIER TELEMATIQUE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_dzv',
            field=models.CharField(blank=True, max_length=200, verbose_name='AIDE A LA CONDUITE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='attribut_gg8',
            field=models.CharField(blank=True, max_length=200, verbose_name='PAYS PROGRAMME (ICP)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_date_debut_garantie',
            field=models.CharField(blank=True, max_length=200, verbose_name='Date d?but garantie'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_date_entree_montage',
            field=models.CharField(blank=True, max_length=200, verbose_name='Date entr?e montage'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_genre_de_produit',
            field=models.CharField(blank=True, max_length=200, verbose_name='GENRE_DE_PRODUIT'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_ligne_de_produit',
            field=models.CharField(blank=True, max_length=200, verbose_name='LIGNE_DE_PRODUIT'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_marque_commerciale',
            field=models.CharField(blank=True, max_length=200, verbose_name='MARQUE_COMMERCIALE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_moteur',
            field=models.CharField(blank=True, max_length=200, verbose_name='MOTEUR'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_silhouette',
            field=models.CharField(blank=True, max_length=200, verbose_name='SILHOUETTE'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='donnee_transmission',
            field=models.CharField(blank=True, max_length=200, verbose_name='TRANSMISSION'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM HARD - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI HARD - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO HARD - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14j',
            field=models.CharField(blank=True, max_length=200, verbose_name='CLIM HARD - Climatisation'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14k',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMB HARD - Combine Planche de Bord'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14l',
            field=models.CharField(blank=True, max_length=200, verbose_name='EMF HARD - Ecran Multifonctions'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14r',
            field=models.CharField(blank=True, max_length=200, verbose_name='AAS HARD - Aide Au Stationnement'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_14x',
            field=models.CharField(blank=True, max_length=200, verbose_name='BTEL HARD - Boitier Telematique (radio telephone)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_19h',
            field=models.CharField(blank=True, max_length=200, verbose_name='MDS HARD - Module de service telematique'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_19z',
            field=models.CharField(blank=True, max_length=200, verbose_name='FMUX_HARD - FAÇADE MULTIPLEXÉ'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_34a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM SOFT LIVRE - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_44a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM FOURN.NO.SERIE - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_44b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI FOURN.NO.SERIE - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_44f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO FOURN.NO.SERIE - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_44l',
            field=models.CharField(blank=True, max_length=200, verbose_name='EMF FOURN.NO.SERIE - Ecran Multifonctions'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_44x',
            field=models.CharField(blank=True, max_length=200, verbose_name='BTEL FOURN.NO.SERIE - Boitier Telematique (radio telephone)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_49h',
            field=models.CharField(blank=True, max_length=200, verbose_name='MDS FOURN.NO.SERIE - Module de service telematique'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_54a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM FOURN.DATE.FAB - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_54b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI FOURN.DATE.FAB - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_54f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO FOURN.DATE.FAB - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_54k',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMB FOURN.DATE.FAB - Combine Planche de Bord'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_54l',
            field=models.CharField(blank=True, max_length=200, verbose_name='EMF FOURN.DATE.FAB - Ecran Multifonctions'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_64a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM FOURN.CODE - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_64b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI FOURN.CODE - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_64f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO FOURN.CODE - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_64x',
            field=models.CharField(blank=True, max_length=200, verbose_name='BTEL FOURN.CODE - Boitier Telematique (radio telephone)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_69h',
            field=models.CharField(blank=True, max_length=200, verbose_name='MDS FOURN.CODE - Module de service telematique'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_84a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM DOTE - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_84b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI DOTE - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_84f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO DOTE - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_84l',
            field=models.CharField(blank=True, max_length=200, verbose_name='EMF DOTE - Ecran Multifonctions'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_84x',
            field=models.CharField(blank=True, max_length=200, verbose_name='BTEL DOTE - Boitier Telematique (radio telephone)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_89h',
            field=models.CharField(blank=True, max_length=200, verbose_name='MDS DOTE - Module de service telematique'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_94a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM SOFT - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_94b',
            field=models.CharField(blank=True, max_length=200, verbose_name='BSI SOFT - Boitier Servitude Intelligent'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_94f',
            field=models.CharField(blank=True, max_length=200, verbose_name='RADIO SOFT - Recepteur Radio'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_94l',
            field=models.CharField(blank=True, max_length=200, verbose_name='EMF SOFT - Ecran Multifonctions'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_94x',
            field=models.CharField(blank=True, max_length=200, verbose_name='BTEL SOFT - Boitier Telematique (radio telephone)'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_99h',
            field=models.CharField(blank=True, max_length=200, verbose_name='MDS SOFT - Module de service telematique'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='electronique_p4a',
            field=models.CharField(blank=True, max_length=200, verbose_name='CMM EOBD - Calculateur Moteur Multifonction'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='organes_10',
            field=models.CharField(blank=True, max_length=200, verbose_name='MOTEUR'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='organes_20',
            field=models.CharField(blank=True, max_length=200, verbose_name='BOITE DE VITESSES'),
        ),
    ]
