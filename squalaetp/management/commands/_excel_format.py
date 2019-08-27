from __future__ import unicode_literals
from xlwt import Workbook
import io
from xlrd import XLRDError
import pandas as pd
import unicodedata
import re
import os


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
        for col_date, col_format in columns.items():
            self.sheet[col_date] = pd.to_datetime(self.sheet[col_date], errors='coerce', format=col_format, utc=True)
        self.sheet.fillna('', inplace=True)

    def _columns_convert(self, digit=True):
        """
        Convert the names of the columns to be used by the database
        :param columns:
            List of column names
        :param digit:
            Remove digits from the column names
        :return:
            list of modified column names
        """
        new_columns = {}
        for column in self.columns:
            name = unicodedata.normalize('NFKD', column).encode('ASCII', 'ignore').decode('utf8').lower()
            name = re.sub(r"[^\w\s]+", "", name)
            if not digit:
                name = ''.join(i for i in name if not i.isdigit())
            name = re.sub(r"[\s]+", "_", name)
            new_columns[column] = name
        self.sheet.rename(columns=new_columns, inplace=True)
        self.columns = list(self.sheet.columns)

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
        basename = os.path.basename(filename[:filename.find('.')])
        xldoc.save('/tmp/{}_reformat.xls'.format(basename))
        df = pd.read_excel("/tmp/{}_reformat.xls".format(basename), sheet_name="Sheet1", skiprows=skip_rows)
        dataframe = df.drop(df[(df['N° de dossier'].isnull()) | (df['N° de dossier'] == 'N° de dossier')].index)
        dataframe.reset_index(drop=True, inplace=True)
        print("File : {}.xls - Row number : {}".format(basename, dataframe.shape[0]))
        return dataframe


class ExcelSqualaetp(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""

    XELON_COLS = ['numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule']

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
        self._columns_convert()

    def xelon_table(self):
        """
        Extracting data for the Xelon table from the Database
        :return:
            list of dictionnaries that represents the data for Xelon table
        """
        data = []
        for line in range(self.nrows):
            data.append(dict(self.sheet.loc[line, self.XELON_COLS]))
        return data

    def corvet_table(self, attribut_file):
        data = []
        drop_col = self.XELON_COLS
        drop_col.remove("vin")
        df_attributs = pd.read_excel(attribut_file, 1, converters={'cle2': str})
        df_corvet = self.sheet.drop(drop_col, axis='columns').fillna("")
        self._add_attributs(df_corvet, df_attributs)
        for line in range(self.nrows):
            df_corvet = self.sheet.drop(drop_col, axis='columns')
            row = df_corvet.loc[line]  # get the data in the ith row
            # print(dict(row))
            if re.match(r'^VF[37]\w{14}$', str(row[0])) and row[1] != "#":
                data.append(dict(row))
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
            vin = self.sheet.at[line, "vin"]
            data_corvet = self.sheet.loc[line, corvet_cols]
            if re.match(r'^VF[37]\w{14}$', str(vin)) and data_corvet[0] != "#":
                corvet_dict = dict(zip(corvet_cols, data_corvet))
                row_dict = dict(zip(["vin", "data"], [vin, corvet_dict]))
                data.append(row_dict)
        return data

    def _add_attributs(self, df_corvet, df_attributs):
        new_columns = {}
        for col in df_corvet.columns:
            col_upper = col.upper()
            if len(df_attributs[df_attributs.cle2 == col_upper]) != 0:
                new_columns[col] = list(df_attributs.loc[df_attributs.cle2 == col_upper].cle1)[0] + "_" + col
            elif len(df_attributs[df_attributs.libelle == col_upper]) != 0:
                new_columns[col] = list(df_attributs.loc[df_attributs.libelle == col_upper].cle1)[0] + "_" + col
            else:
                new_columns[col] = col
        self.sheet.rename(columns=new_columns, inplace=True)
        self.sheet.rename(str.lower, axis='columns', inplace=True)
        self.columns = list(self.sheet.columns)


class ExcelsDelayAnalysis(ExcelFormat):
    """## Read data in Excel file for Delay Analysis ##"""

    DROP_COLS = ['ref_produit_commerciale', 'ref_produit_clarion', 'code_pdv', 'nom_pdv',
                 'date_daccord_de_la_demande', 'delai_prevu_sp', 'nom_equipe', 'n_commande_de_travaux']
    COLS_DATE = {'date_retour': "'%d/%m/%Y", 'date_de_cloture': "'%d/%m/%Y %H:%M:%S"}

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
        self._columns_convert(digit=False)
        self.sheet.replace({"Oui": 1, "Non": 0}, inplace=True)
        self.sheet.drop(columns=self.DROP_COLS, inplace=True)
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
        row_index = self.sheet[self.sheet['n_de_dossier'] == file_number].index
        if list(row_index):
            row_dict = dict(self.sheet.loc[row_index[0]])
            row_dict = self.del_empty_dates(row_dict)
            del row_dict["n_de_dossier"]
        return row_dict

    def table(self):
        """
        Extracting data for the table from the Database
        :return:
            list of dictionnaries that represents the data for table
        """
        data = []
        for line in range(self.nrows):
            data.append(self.del_empty_dates(dict(self.sheet.loc[line])))
        return data

    @staticmethod
    def del_empty_dates(data):
        if not data["date_de_cloture"]:
            del data["date_de_cloture"]
        return data
