from squalaetp.models import Xelon


def products_count():
    labels = ["RT6/RNEG2", "SMEG", "RNEG", "NG4", "DISPLAY", "RTx"]
    prod_nb = []
    rtx_nb = 0
    for prod in labels:
        if prod in ["DISPLAY", "SMEG"]:
            prod_nb.append(Xelon.objects.filter(modele_produit__icontains=prod, date_retour__isnull=False).count())
        elif prod == "RTx":
            for rtx in ["RT3", "RT4", "RT5"]:
                rtx_nb += Xelon.objects.filter(modele_produit=rtx, date_retour__isnull=False).count()
        else:
            prod_nb.append(Xelon.objects.filter(modele_produit=prod, date_retour__isnull=False).count())
    prod_nb.append(rtx_nb)
    labels_nb = sum(prod_nb)
    prod_nb.append(Xelon.objects.filter(date_retour__isnull=False).count() - labels_nb)
    labels.append("AUTRES")
    return labels, prod_nb