from squalaetp.models import Corvet
from utils.file.export import ExportExcel


def extract_ecu(vin_list=None):
    filename = 'ecu'
    header = [
        'Numero de dossier', 'V.I.N.', 'Modele produit', 'DATE_DEBUT_GARANTIE', '14A_CMM_HARD', '34A_CMM_SOFT_LIVRE',
        '94A_CMM_SOFT', '44A_CMM_FOURN.NO.SERIE', '54A_CMM_FOURN.DATE.FAB', '64A_CMM_FOURN.CODE', '84A_CMM_DOTE',
        'P4A_CMM_EOBD'
    ]
    corvets = Corvet.objects.filter(vin__in=vin_list)

    values_list = (
        'xelons__numero_de_dossier', 'vin', 'xelons__modele_produit', 'donnee_date_debut_garantie', 'electronique_14a',
        'electronique_34a', 'electronique_94a', 'electronique_44a', 'electronique_54a',
        'electronique_64a', 'electronique_84a', 'electronique_p4a'
    )

    return ExportExcel(queryset=corvets, filename=filename, header=header, values_list=values_list).http_response()
