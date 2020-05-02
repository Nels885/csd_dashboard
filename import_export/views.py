from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.db.models.functions import Cast, TruncSecond
from django.db.models import DateTimeField, CharField
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDictKeyError
from django.core.management import call_command

from squalaetp.models import Xelon, Corvet
from reman.models import Batch, Repair
from .forms import ExportCorvetForm, ExportRemanForm
from utils.file.export import export_csv
from utils.file import handle_uploaded_file
from pandas.errors import ParserError


def export_corvet(request):
    form = ExportCorvetForm(request.POST or None)
    if form.is_valid():
        if request.user.has_perm('squalaetp.change_corvet'):
            product = form.cleaned_data['products']
            if product in ['corvet', 'ecu', 'bsi', 'com']:
                return redirect('import_export:export_{}_csv'.format(product))
        messages.warning(request, _('You do not have the required permissions'))
    return redirect(request.META.get('HTTP_REFERER'))


def export_reman(request):
    form = ExportRemanForm(request.POST or None)
    if form.is_valid():
        if request.user.has_perms('reman.view_batch', 'reman.view_repair'):
            table = form.cleaned_data['tables']
            if table in ['batch', 'repair']:
                return redirect('import_export:export_{}_csv'.format(table))
        messages.warning(request, _('You do not have the required permissions'))
    return redirect(request.META.get('HTTP_REFERER'))


@permission_required('squalaetp.change_corvet')
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


@permission_required('squalaetp.change_corvet')
def export_ecu_csv(request):
    filename = 'ecu'
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD', '34A_CMM_SOFT_LIVRE',
        '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB', '64A_CMM_FOURN.CODE', '84A_CMM_DOTE',
        'P4A_CMM_EOBD'
    ]
    ecus = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14a__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'modele_produit', 'date_debut_garantie', 'corvet__electronique_14a',
        'corvet__electronique_34a', 'corvet__electronique_94a', 'corvet__electronique_44a', 'corvet__electronique_54a',
        'corvet__electronique_64a', 'corvet__electronique_84a', 'corvet__electronique_p4a'
    )

    return export_csv(queryset=ecus, filename=filename, header=header, values_list=values_list)


@permission_required('squalaetp.change_corvet')
def export_bsi_csv(request):
    filename = 'bsi'
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'DATE_DEBUT_GARANTIE', '14B_BSI_HARD', '94B_BSI_SOFT',
        '44B_BSI_FOURN.NO.SERIE', '54B_BSI_FOURN.DATE.FAB', '64B_BSI_FOURN.CODE', '84B_BSI_DOTE'
    ]

    bsis = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_14b__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'modele_produit', 'date_debut_garantie', 'corvet__electronique_14b',
        'corvet__electronique_94b', 'corvet__electronique_44b', 'corvet__electronique_54b', 'corvet__electronique_64b',
        'corvet__electronique_84b',
    )

    return export_csv(queryset=bsis, filename=filename, header=header, values_list=values_list)


@permission_required('squalaetp.change_corvet')
def export_com_csv(request):
    filename = 'com200x'
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'DATE_DEBUT_GARANTIE', '16P_HDC_HARD',
        '46P_HDC_FOURN.NO.SERIE', '56P_HDC_FOURN.DATE.FAB', '66P_HDC_FOURN.CODE'
    ]

    bsis = Xelon.objects.filter(corvet__isnull=False).exclude(corvet__electronique_16p__exact='').annotate(
        date_debut_garantie=Cast(TruncSecond('corvet__donnee_date_debut_garantie', DateTimeField()), CharField())
    )
    values_list = (
        'numero_de_dossier', 'vin', 'modele_produit', 'date_debut_garantie', 'corvet__electronique_16p',
        'corvet__electronique_46p', 'corvet__electronique_56p', 'corvet__electronique_66p'
    )

    return export_csv(queryset=bsis, filename=filename, header=header, values_list=values_list)


@permission_required('reman.view_batch')
def export_batch_csv(request):
    filename = 'batch_reman'
    header = [
        'Numero de lot', 'Quantite', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'Fabriquant', 'Date_de_Debut',
        'Date_de_fin', 'Actif', 'Ajoute par', 'Ajoute le'
    ]
    batch = Batch.objects.all().order_by('batch_number')
    values_list = (
        'batch_number', 'quantity', 'ecu_model__es_reference', 'ecu_model__technical_data', 'ecu_model__hw_reference',
        'ecu_model__supplier_oe', 'start_date', 'end_date', 'active', 'created_by__username', 'created_at'
    )
    return export_csv(queryset=batch, filename=filename, header=header, values_list=values_list)


@permission_required('reman.view_repair')
def export_repair_csv(request):
    filename = 'repair_reman'
    header = [
        'Numero_identification', 'Numero_lot', 'Ref_REMAN', 'Type_ECU', 'HW_Reference', 'SW_Reference', 'Fabriquant',
        'Remarque', 'Cree_le', 'Modifie_par', 'Date_de_cloture'
    ]
    batch = Repair.objects.all().order_by('identify_number')
    values_list = (
        'identify_number', 'batch__batch_number', 'batch__ecu_model__es_reference', 'batch__ecu_model__technical_data',
        'batch__ecu_model__hw_reference', 'batch__ecu_model__sw_reference', 'batch__ecu_model__supplier_oe',
        'remark', 'created_at', 'modified_by__username', 'closing_date'
    )
    return export_csv(queryset=batch, filename=filename, header=header, values_list=values_list)


@permission_required('reman.add_sparepart', 'reman.change_sparepart')
def import_sparepart(request):
    if request.method == 'POST':
        try:
            if request.FILES["myfile"]:
                my_file = request.FILES["myfile"]
                file_url = handle_uploaded_file(my_file)
                call_command("spareparts", "--file", file_url)
                messages.success(request, 'Upload terminé !')
                return redirect('reman:part_table')
        except MultiValueDictKeyError:
            messages.warning(request, 'Le fichier est absent !')
        except (UnicodeDecodeError, ParserError):
            messages.warning(request, 'Format de fichier incorrect !')
        except KeyError:
            messages.warning(request, "Le fichier n'est pas correctement formaté")
    return redirect('reman:import_export')
