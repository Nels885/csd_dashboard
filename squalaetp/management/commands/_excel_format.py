from __future__ import unicode_literals
from xlwt import Workbook
import io
from xlrd import XLRDError
import pandas as pd
import unicodedata
import re


class ExcelFormat:
    """## Base class for formatting Excel files ##"""

    def __init__(self, file, sheet_index, columns, skip_rows=None):
        """
        Initialize ExcelFormat class
        :param file:
            Excel file path
        :param sheet_index:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        :param skip_rows:
            Rows to skip at the beginning (0-indexed)
        """
        try:
            df = pd.read_excel(file, sheet_index, skiprows=skip_rows)
        except XLRDError:
            df = self._excel_decode(file, skip_rows)
        df.dropna(how='all', inplace=True)
        self.sheet = df.fillna('')
        self.nrows = self.sheet.shape[0]
        self.columns = list(self.sheet.columns[:columns])

    def read_all(self):
        """
        Formatting data from the excel file
        :return:
            list of dictionaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.row_values(line)  # get the data in the ith row
            row_dict = dict(zip(self.columns, row))
            data.append(row_dict)
        return data

    def _date_converter(self, columns):
        """
        Converting columns to datetime
        :param columns:
            list of columns to convert
        """
        for col_date in columns:
            self.sheet[col_date] = pd.to_datetime(self.sheet[col_date], errors='coerce', utc=True)
        self.sheet.fillna(pd.Timestamp(2019, 1, 1), inplace=True)

    @staticmethod
    def _columns_convert(columns):
        """
        Convert the names of the columns to be used by the database
        :param columns:
            List of column names
        :return:
            list of modified column names
        """
        data = []
        deletion = {' ': '_', '.': ''}
        for column in columns:
            name = unicodedata.normalize('NFKD', column).encode('ASCII', 'ignore').decode('utf8').lower()
            for old, new in deletion.items():
                name = name.replace(old, new)
            data.append(name)
        return data

    @staticmethod
    def _excel_decode(filename, skip_rows):
        """
        Fix badly formatted excel files
        :param filename:
            Excel file path
        :param skip_rows:
            Rows to skip at the beginning (0-indexed)
        :return:
            Temporary Excel file in the 'tmp' directory
        """
        file1 = io.open(filename, 'r', encoding='latin3')
        data = file1.readlines()

        # Creating a workbook object
        xldoc = Workbook()
        # Adding a sheet to the workbook object
        sheet = xldoc.add_sheet("Sheet1", cell_overwrite_ok=True)
        # Iterating and saving the data to sheet
        for i, row in enumerate(data):
            # Two things are done here
            # Removeing the '\n' which comes while reading the file using io.open
            # Getting the values after splitting using '\t'
            for j, val in enumerate(row.replace('\n', '').split('\t')):
                sheet.write(i, j, val)

        # Saving the file as an excel file
        xldoc.save('/tmp/reformat.xls')
        return pd.read_excel("/tmp/reformat.xls", sheet_name="Sheet1", skiprows=skip_rows)


class ExcelSqualaetp(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""

    XELON_COLS = ['Numéro de dossier', 'V.I.N.', 'Modèle produit', 'Modèle véhicule']

    def __init__(self, file, sheet_index=0, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_index:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super().__init__(file, sheet_index, columns)

    def xelon_table(self):
        """
        Extracting data for the Xelon table from the Database
        :return:
            list of dictionnaries that represents the data for Xelon table
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line, self.XELON_COLS]  # get the data in the ith row
            row_dict = dict(zip(self._columns_convert(self.XELON_COLS), row))
            data.append(row_dict)
        return data

    def corvet_table(self, attribut_file):
        data, columns = [], []
        drop_col = self.XELON_COLS
        drop_col.remove("V.I.N.")
        df_attributs = pd.read_excel(attribut_file, 1, converters={'cle2': str})
        df_corvet = self.sheet.drop(drop_col, axis='columns').fillna("")
        for col in df_corvet.columns:
            if len(df_attributs[df_attributs.cle2 == col]) != 0:
                columns.append(list(df_attributs.loc[df_attributs.cle2 == col].cle1)[0] + "_" + col)
            elif len(df_attributs[df_attributs.libelle == col]) != 0:
                columns.append(list(df_attributs.loc[df_attributs.libelle == col].cle1)[0] + "_" + col)
            else:
                columns.append(col)
        for line in range(self.nrows):
            row = df_corvet.loc[line]  # get the data in the ith row
            if re.match(r'^VF[37]\w{14}$', str(row[0])) and row[1] != "#":
                row_dict = dict(zip(self._columns_convert(columns), row))
                data.append(row_dict)
        return data

    def corvet_backup_table(self):
        """
        Extracting data for the Corvet Backup table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet Backup table
        """
        data = []
        corvet_cols = self.columns[4:]
        for line in range(self.nrows):
            vin = self.sheet.at[line, "V.I.N."]
            data_corvet = self.sheet.loc[line, corvet_cols]
            if re.match(r'^VF[37]\w{14}$', str(vin)) and data_corvet[0] != "#":
                corvet_dict = dict(zip(corvet_cols, data_corvet))
                row_dict = dict(zip(["vin", "data"], [vin, corvet_dict]))
                data.append(row_dict)
        return data


class ExcelsDelayAnalysis(ExcelFormat):
    """## Read data in Excel file for Delay Analysis ##"""

    COLS = ['Date Retour', 'Lieu de stockage', 'Date de clôture', 'Type de clôture', 'Nom Technicien',
            'Commentaire SAV Admin', 'Commentaire de la FR', 'Commentaire action', 'Libellé de la fiche cas',
            'Dossier VIP', 'Express']
    COLS_DATE = ['Date Retour', 'Date de clôture']

    def __init__(self, file, sheet_index=0, columns=None):
        """
        Initialize ExcelDelayAnalysis class
        :param file:
            excel file to process
        :param sheet_index:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super().__init__(file, sheet_index, columns, skip_rows=8)
        self.sheet.replace({"Oui": 1, "Non": 0}, inplace=True)
        self._date_converter(self.COLS_DATE)

    def xelon_table(self, file_number):
        """
        Extracting data for the Xelon table from the Database
        :param file_number:
            File number to search
        :return:
            Dictionnary that represents the data of file number to insert Xelon table
        """
        row_dict = {}
        row_index = self.sheet[self.sheet['N° de dossier'] == file_number].index
        row = self.sheet.loc[row_index, self.COLS]  # get the data in the ith row
        if len(row):
            row_dict = dict(zip(self._columns_convert(self.COLS), row.values[0]))
        return row_dict
