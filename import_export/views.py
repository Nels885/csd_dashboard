from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField

from squalaetp.models import Xelon, Corvet
from utils.django.decorators import group_required
from utils.file.export import export_csv


@group_required('cellule', 'technician')
def export_corvet_csv(request):
    filename = 'corvet'
    header = [
        'V.I.N.', 'DATE_DEBUT_GARANTIE', 'DATE_ENTREE_MONTAGE', 'LIGNE_DE_PRODUIT', 'MARQUE_COMMERCIALE', 'SILHOUETTE',
        'GENRE_DE_PRODUIT', 'DDO', 'DGM', 'DHB', 'DHG', 'DJQ', 'DJY', 'DKX', 'DLX', 'DOI', 'DQM', 'DQS', 'DRC', 'DRT',
        'DTI', 'DUN', 'DWL', 'DWT', 'DXJ', 'DYB', 'DYM', 'DYR', 'DZV', 'GG8', '14F', '14J', '14K', '14L', '14R', '14X',
        '19Z', '44F', '44L', '44X', '54F', '54K', '54L', '84F', '84L', '84X', '94F', '94L', '94X', 'DAT', 'DCX', '19H',
        '49H', '64F', '64X', '69H', '89H', '99H', '14A', '34A', '44A', '54A', '64A', '84A', '94A', 'P4A', 'MOTEUR',
        'TRANSMISSION', '10', '14B', '20', '44B', '54B', '64B', '84B', '94B', '16P', '46P', '56P', '66P'
    ]
    corvets = Corvet.objects.all()

    return export_csv(queryset=corvets, filename=filename, header=header)


@group_required('cellule', 'technician')
def export_ecu_csv(request):
    filename = 'ecu'
    header = [
        'Numero de dossier', 'V.I.N.', 'DATE_DEBUT_GARANTIE', '14A', '34A', '94A', '44A', '54A', '64A', '84A', 'P4A'
    ]
    ecus = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14a__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'date_debut_garantie', 'corvet__electronique_14a', 'corvet__electronique_34a',
        'corvet__electronique_94a', 'corvet__electronique_44a', 'corvet__electronique_54a', 'corvet__electronique_64a',
        'corvet__electronique_84a', 'corvet__electronique_p4a'
    )

    return export_csv(queryset=ecus, filename=filename, header=header, values_list=values_list)


@group_required('cellule', 'technician')
def export_bsi_csv(request):
    filename = 'bsi'
    header = ['Numero de dossier', 'V.I.N.', 'DATE_DEBUT_GARANTIE', '14B', '94B', '44B', '54B', '64B', '84B']

    bsis = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14b__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'date_debut_garantie', 'corvet__electronique_14b', 'corvet__electronique_94b',
        'corvet__electronique_44b', 'corvet__electronique_54b', 'corvet__electronique_64b', 'corvet__electronique_84b',
    )

    return export_csv(queryset=bsis, filename=filename, header=header, values_list=values_list)


@group_required('cellule', 'technician')
def export_com_csv(request):
    filename = 'com200x'
    header = ['Numero de dossier', 'V.I.N.', 'DATE_DEBUT_GARANTIE', '16P', '46P', '56P', '66P']

    bsis = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_16p__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'date_debut_garantie', 'corvet__electronique_16p', 'corvet__electronique_46p',
        'corvet__electronique_56p', 'corvet__electronique_66p'
    )

    return export_csv(queryset=bsis, filename=filename, header=header, values_list=values_list)
