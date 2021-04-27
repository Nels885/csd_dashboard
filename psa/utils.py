from utils.file.export import ExportExcel

from psa.models import Multimedia
from psa.templatetags.corvet_tags import get_corvet


class ExportCorvetExcel(ExportExcel):
    COL_CORVET = {
        'corvet__donnee_ligne_de_produit': 'DON_LIN_PROD', 'corvet__donnee_silhouette': 'DON_SIL',
        'corvet__donnee_genre_de_produit': 'DON_GEN_PROD', 'corvet__attribut_dhb': 'ATT_DHB',
        'corvet__attribut_dlx': 'ATT_DLX', 'corvet__attribut_dun': 'ATT_DUN', 'corvet__attribut_dym': 'ATT_DYM',
        'corvet__attribut_dyr': 'ATT_DYR'
    }

    def __init__(self, values_list, fields, filename, header, excel_type):
        super(ExportCorvetExcel, self).__init__(values_list, filename, header, excel_type)
        self.fields = fields
        new_list = []
        for data_tuple in self.valueSet:
            data_list = [value for value in data_tuple]
            data_tuple = self.get_multimedia_display(data_list)
            new_list.append(self.get_corvet_display(data_list))
        self.valueSet = new_list

    def get_multimedia_display(self, data_list):
        if 'corvet__btel__name' in self.fields:
            position = self.fields.index('corvet__btel__name')
            for prod in Multimedia.PRODUCT_CHOICES:
                if prod[0] == data_list[position]:
                    data_list[position] = prod[1]
                    break
        return data_list

    def get_corvet_display(self, data_list):
        for field, arg in self.COL_CORVET.items():
            if field in self.fields:
                position = self.fields.index(field)
                if data_list[position]:
                    if arg == 'DON_LIN_PROD':
                        if 'vin' in self.fields and 'VF3' in data_list[self.fields.index('vin')]:
                            arg = 'DON_LIN_PROD 0'
                        elif 'vin' in self.fields and 'VF3' in data_list[self.fields.index('vin')]:
                            arg = 'DON_LIN_PROD 1'
                    data_list[position] = f"{data_list[position]} - {get_corvet(data_list[position], arg)}"
        return data_list
