from squalaetp.models import Xelon


def products_count():
    """
    Function to count the number of products to repair
    :return:
        list of name and number of different products
    """
    labels = ["RT6/RNEG2", "SMEG", "RNEG", "NG4", "DISPLAY", "RTx", "CALC MOT", "BSI", 'NISSAN']
    prod_nb = []
    rtx_nb = 0
    pending_prod = Xelon.objects.filter(delai_au_en_jours_calendaires__isnull=False,
                                        delai_au_en_jours_calendaires__lt=30,
                                        type_de_cloture='')
    for prod in labels:
        if prod in ["DISPLAY", "SMEG", "NISSAN"]:
            prod_nb.append(pending_prod.filter(modele_produit__icontains=prod).count())
        elif prod == "RTx":
            for rtx in ["RT3", "RT4", "RT5"]:
                rtx_nb += pending_prod.filter(modele_produit=rtx).count()
        elif prod in ["CALC MOT", "BSI"]:
            prod_nb.append(pending_prod.filter(famille_produit=prod).count())
        else:
            prod_nb.append(pending_prod.filter(modele_produit=prod).count())
    prod_nb.append(rtx_nb)
    labels_nb = sum(prod_nb)
    prod_nb.append(pending_prod.count() - labels_nb)
    labels.append("AUTRES")
    return labels, prod_nb
