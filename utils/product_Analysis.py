from squalaetp.models import Xelon


class ProductAnalysis:
    LABELS = ["RT6/RNEG2", "SMEG", "RNEG", "NG4", "DISPLAY", "RTx", "CALC MOT", "BSI", 'NISSAN', "AUTRES"]

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueries = Xelon.objects.filter(
            delai_au_en_jours_calendaires__lt=30).exclude(lieu_de_stockage='MAGATTREPA/ZONECE', ilot='LaboQual')
        self.pending = self.pendingQueries.filter(type_de_cloture__in=['', 'Sauvée']).count()
        self.late = self._late_products()
        self.percent = int(self._percent_of_late_products())
        self.listProds = [
            ["RT6/RNEG2", "text-primary"],
            ["SMEG", "text-success"],
            ["RNEG", "text-danger"],
            ["NG4", "text-secondary"],
            ["DISPLAY", "text-dark"],
            ["RTx", "text-info"],
            ["AUTRES", "text-warning"]
        ]

    def _percent_of_late_products(self):
        """
        Calculating the percentage of late products
        :return:
            result
        """
        if self.pending:
            return (self.late / self.pending) * 100
        else:
            return 0

    def _late_products(self):
        """
        Calculating of the number of late products
        :return:
            result
        """
        return self.pendingQueries.filter(delai_au_en_jours_calendaires__gt=3, type_de_cloture='').count()

    def products_count(self):
        """
        Function to count the number of products to repair
        :return:
            list of name and number of different products
        """
        prod_nb, rtx_nb = [], 0
        pending_prod = self.pendingQueries.filter(type_de_cloture__in=['', 'Sauvée'])
        for prod in self.LABELS[:-1]:
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
        return self.LABELS, prod_nb
