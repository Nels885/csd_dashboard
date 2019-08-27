from squalaetp.models import Xelon


class ProductAnalysis:

    def __init__(self):
        """
        Initialization of the ProductAnalysis class
        """
        self.pending = Xelon.objects.filter(delai_au_en_jours_ouvres__isnull=False,
                                            delai_au_en_jours_ouvres__lt=30,
                                            date_de_cloture__isnull=True).count()
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
        return (self.pending / 100) * self.late

    @staticmethod
    def _late_products():
        """
        Calculating of the number of late products
        :return:
            result
        """
        prods = Xelon.objects.filter(
            delai_au_en_jours_ouvres__gt=3, express=True, date_de_cloture__isnull=True).count()
        prods = Xelon.objects.filter(
            delai_au_en_jours_ouvres__gt=5, express=False, date_de_cloture__isnull=True).count() + prods
        return prods
