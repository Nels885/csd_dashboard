from squalaetp.models import Xelon


class ProductAnalysis:

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pendingQueries = Xelon.objects.filter(delai_au_en_jours_calendaires__isnull=False,
                                                   delai_au_en_jours_calendaires__lte=30,
                                                   type_de_cloture='').exclude(lieu_de_stockage='MAGATTREPA/ZONECE')
        self.pending = self.pendingQueries.count()
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
        return self.pendingQueries.filter(delai_au_en_jours_calendaires__gt=3).count()
