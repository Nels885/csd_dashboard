import pandas as pd
import unicodedata
import re


class ExcelSqualaetp:
    """## Read data in Excel file for Squalaetp ##"""
    XELON_COLS = ['Numéro de dossier', 'V.I.N.', 'Modèle produit', 'Modèle véhicule']

    def __init__(self, file, sheet_index=0, columns=None):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        df = pd.read_excel(file, sheet_index)
        df.dropna(how='all', inplace=True)
        self.sheet = df.fillna('')
        self.nrows = self.sheet.shape[0]
        self.columns = list(self.sheet.columns[:columns])

    def read_all(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.row_values(line)  # get the data in the ith row
            row_dict = dict(zip(self.columns, row))
            data.append(row_dict)
        return data

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
