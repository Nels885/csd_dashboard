import logging

from utils.microsoft_format import ExcelFormat

logger = logging.getLogger('command')


class ExcelSqualaetp(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""
    CORVET_DROP_COLS = ['numero_de_dossier', 'modele_produit', 'modele_vehicule', 'telecodage', 'appairage']
    XELON_COLS = CORVET_DROP_COLS + ['vin']
    COLS_DATE = {'date_debut_garantie': "%d/%m/%Y %H:%M:%S", 'date_entree_montage': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            super(ExcelSqualaetp, self).__init__(file, sheet_name, columns, datedelta=0, offdays=[5, 6])
            self._columns_convert()
            self.sheet.replace({"#": None}, inplace=True)
            self._date_converter(self.COLS_DATE)
        except FileNotFoundError as err:
            self.ERROR = f'FileNotFoundError: {err}'
            logger.error(self.ERROR)

    def read(self, add_fields=None):
        """
        Extracting data for the Xelon table from the Database
        :param add_fields:
            Adding fields to list of dictionaries that represents the data for Xelon table
        :return:
            list of dictionaries that represents the data for Xelon table
        """
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                row = dict(self.sheet.loc[line, self._columns_check(self.XELON_COLS)].dropna())
                if isinstance(add_fields, dict):
                    row.update(add_fields)
                data.append(row)
        return data

    def xelon_number_list(self):
        if not self.ERROR:
            return self.sheet['numero_de_dossier']
        else:
            return list()
