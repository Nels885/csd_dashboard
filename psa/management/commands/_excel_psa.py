import logging
from utils.microsoft_format import ExcelFormat, pd

from psa.models import CorvetAttribute

logger = logging.getLogger('command')


class ExcelCorvet(ExcelFormat):
    """## Read data in Excel file for Corvet ##"""
    ERROR = False
    CORVET_DROP_COLS = ['numero_de_dossier', 'modele_produit', 'modele_vehicule']
    COLS_DATE = {'date_debut_garantie': "%d/%m/%Y %H:%M:%S", 'date_entree_montage': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelCorvet class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            super(ExcelCorvet, self).__init__(file, sheet_name, columns, dtype=str)
            self._columns_convert()
            self.sheet.replace({"#": None}, inplace=True)
            self._date_converter(self.COLS_DATE)
            df_corvet = self.sheet.drop(self.CORVET_DROP_COLS, axis='columns')
            self._add_attributs(df_corvet)
        except FileNotFoundError as err:
            logger.error(f'FileNotFoundError: {err}')
            self.ERROR = True

    def read(self):
        """
        Extracting data for the Corvet table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet table
        """
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                row = self.sheet.loc[line]  # get the data in the ith row
                if row[0] and isinstance(row[2], pd.Timestamp):
                    data.append(dict(row.dropna()))
        return data

    def backup(self):
        """
        Extracting data for the Corvet Backup table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet Backup table
        """
        data = []
        if not self.ERROR:
            for row in self.read():
                vin = row['vin']
                data.append({'vin': vin, 'data': row})
        return data

    def _add_attributs(self, df_corvet):
        new_columns = {}
        attributes = CorvetAttribute.objects.all()
        for col in df_corvet.columns:
            if attributes.filter(key_2__iexact=col):
                new_columns[col] = f"{attributes.filter(key_2__iexact=col).first().key_1}_{col}"
            elif attributes.filter(label__iexact=col):
                new_columns[col] = f"{attributes.filter(label__iexact=col).first().key_1}_{col}"
            else:
                new_columns[col] = col
        df_corvet.rename(columns=new_columns, inplace=True)
        self.sheet = df_corvet.rename(str.lower, axis='columns')
        self.columns = list(self.sheet.columns)
        self.nrows = self.sheet.shape[0]


class ExcelCorvetAttribute(ExcelFormat):
    """## Read data in Excel file for Attributs CORVET.xlsx ##"""
    ERROR = False
    COLS = {"clé1": "key_1", "clé2": "key_2", "libelle": "label", "colext": "col_ext"}

    def __init__(self, file, sheet_name=1, columns=None):
        """
        Initialize ExcelCorvetAttribute class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            super(ExcelCorvetAttribute, self).__init__(file, sheet_name, columns)
            self._columns_rename(self.COLS)
            self.sheet.replace({"": None, "#": None}, inplace=True)
        except FileNotFoundError as err:
            logger.error(f'FileNotFoundError: {err}')
            self.ERROR = True

    def read(self):
        """
        Extracting data for the Suptech table form the Database
        :return:
            list of dictionnaries that represents the data for Suptech table
        """
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                try:
                    row = {'id': (line + 1)}
                    row.update(dict(self.sheet.loc[line].dropna(how='all')))  # get the data in the ith row
                    data.append(row)
                except KeyError:
                    pass
        return data


class ExcelDefaultCode(ExcelFormat):
    """## Read data in Excel file for PSA_code_defaults.xlsx ##"""
    ERROR = False
    COLS = {
        "A": "code", "B": "description", "C": "type", "D": "characterization", "E": "location", "F": "help",
        "G": "ecu_type"
    }

    def __init__(self, file, sheet_name=0, columns=None, skiprows=None):
        """
        Initialize ExcelDefaultCode class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            cols = ",".join(self.COLS.keys())
            super(ExcelDefaultCode, self).__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=cols)
            self.sheet.dropna(axis='columns', how='all', inplace=True)
            self._columns_rename(self.COLS)
            self.sheet.replace({"": None, "#": None}, inplace=True)
        except FileNotFoundError as err:
            logger.error(f'FileNotFoundError: {err}')
            self.ERROR = True

    def read(self):
        """
        Extracting data for the DefaultCode table form the Database
        :return:
            list of dictionnaries that represents the data for DefaultCode table
        """
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                row = self.sheet.loc[line]  # get the data in the ith row
                data.append(dict(row.dropna()))
        return data
