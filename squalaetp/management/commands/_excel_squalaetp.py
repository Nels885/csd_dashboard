import logging

from utils.microsoft_format import ExcelFormat, pd

logger = logging.getLogger('command')


class ExcelSqualaetp(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""
    ERROR = False
    CORVET_DROP_COLS = ['numero_de_dossier', 'modele_produit', 'modele_vehicule']
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
            super(ExcelSqualaetp, self).__init__(file, sheet_name, columns)
            self._columns_convert()
            self.sheet.replace({"#": None}, inplace=True)
            self._date_converter(self.COLS_DATE)
        except FileNotFoundError as err:
            logger.error(f'FileNotFoundError: {err}')
            self.ERROR = True

    def xelon_table(self):
        """
        Extracting data for the Xelon table from the Database
        :return:
            list of dictionnaries that represents the data for Xelon table
        """
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                row = self.sheet.loc[line, self.XELON_COLS]
                if row[0]:
                    data.append(dict(row.dropna()))
            return data

    def corvet_table(self, attribut_file=None):
        """
        Extracting data for the Corvet table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet table
        """
        data = []
        if not self.ERROR:
            df_corvet = self.sheet.drop(self.CORVET_DROP_COLS, axis='columns')
            df_corvet, nrows = self._add_attributs(df_corvet, attribut_file)
            for line in range(nrows):
                row = df_corvet.loc[line]  # get the data in the ith row
                if row[0] and isinstance(row[2], pd.Timestamp):
                    data.append(dict(row.dropna()))
        return data

    def corvet_backup_table(self):
        """
        Extracting data for the Corvet Backup table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet Backup table
        """
        data = []
        if not self.ERROR:
            for row in self.corvet_table():
                vin = row['vin']
                data.append({'vin': vin, 'data': row})
        return data

    def xelon_number_list(self):
        if not self.ERROR:
            return self.sheet['numero_de_dossier']
        else:
            return list()
