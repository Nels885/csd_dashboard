import logging

from utils.microsoft_format import ExcelFormat

logger = logging.getLogger('command')


class ExcelDelayAnalysis(ExcelFormat):
    """## Read data in Excel file for Delay Analysis ##"""
    DROP_COLS = ['ref_produit_clarion', 'code_pdv', 'nom_pdv', 'date_daccord_de_la_demande', 'delai_prevu_sp',
                 'nom_equipe', 'n_commande_de_travaux', 'delai_expedition_attendue']
    COLS_DATE = {'date_retour': "'%d/%m/%Y", 'date_de_cloture': "'%d/%m/%Y %H:%M:%S",
                 'date_expedition_attendue': "'%d/%m/%Y"}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelDelayAnalysis class
        :param file:
            excel file to process
        :param sheet_index:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            super(ExcelDelayAnalysis, self).__init__(file, sheet_name, columns, skiprows=8, datedelta=0)
            self._drop_lines()
            self.sheet['ilot'] = [self.basename for _ in range(self.nrows)]
            self._columns_convert(digit=False)
            self.sheet.replace({"Oui": 1, "Non": 0}, inplace=True)
            self.sheet.drop(columns=self.DROP_COLS, inplace=True)
            self._date_converter(self.COLS_DATE)
            # dfs.append(self.sheet)
        except FileNotFoundError as err:
            self.ERROR = f'FileNotFoundError: {err}'
            logger.error(self.ERROR)
        except KeyError as err:
            self.ERROR = f'KeyError: {err} in the file : {file}'
            logger.error(self.ERROR)

    def xelon_table(self, file_number):
        """
        Extracting data for the Xelon table from the Database
        :param file_number:
            File number to search
        :return:
            Dictionnary that represents the data of file number to insert Xelon table
        """
        row_dict = {}
        if not self.ERROR:
            row_index = self.sheet[self.sheet['n_de_dossier'] == file_number].index
            if list(row_index):
                row_dict = dict(self.sheet.loc[row_index[0]])
                row_dict = self._key_formatting(row_dict)
        return row_dict

    def table(self):
        """
        Extracting data for the table from the Database
        :return:
            list of dictionnaries that represents the data for table
        """
        data1 = []
        if not self.ERROR:
            data = [self._key_formatting(dict(self.sheet.loc[line].fillna(''))) for line in range(self.nrows)]
            for row in data:
                for key, value in dict(row).items():
                    if not value:
                        del row[key]
                data1.append(row)
        return data1

    def xelon_number_list(self):
        if not self.ERROR:
            return list(self.sheet.get("n_de_dossier", []))
        else:
            return []

    # def _concat_files(self, dfs):
    #     if dfs:
    #         self.sheet = pd.concat(dfs).reset_index(drop=True)
    #         self.nrows = self.sheet.shape[0]
    #         self._columns_convert(digit=False)
    #         self.sheet.replace({"Oui": 1, "Non": 0}, inplace=True)
    #         self.sheet.drop(columns=self.DROP_COLS, inplace=True)
    #         self._date_converter(self.COLS_DATE)
    #     else:
    #         logger.error("No EXCEL files found!")
    #         self.ERROR = True

    @staticmethod
    def _key_formatting(data):
        data["numero_de_dossier"] = data.pop("n_de_dossier")
        data["modele_produit"] = data.pop("ref_produit_commerciale")
        return data

    def _drop_lines(self):
        df = self.sheet
        self.sheet = df.drop(df[(df['N° de dossier'].isnull()) | (df['N° de dossier'] == 'N° de dossier')].index)
        self.sheet.reset_index(drop=True, inplace=True)
        self.nrows = self.sheet.shape[0]


class ExcelTimeLimitAnalysis(ExcelFormat):
    COLS = {'A': 'numero_de_dossier', 'B': 'date_retour', 'D': 'date_de_cloture', 'E': 'type_de_cloture',
            'F': 'nom_technicien', 'M': 'famille_produit'}
    COLS_DATE = {'date_retour': "%d/%m/%Y", 'date_de_cloture': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, sheet_name=0, columns=None, skiprows=2):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        cols = ",".join(self.COLS.keys())
        try:
            super().__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=cols, datedelta=1, offdays=[6, 0])
            self._columns_rename(self.COLS)
            self.sheet.replace({"#": None}, inplace=True)
            self.sheet.fillna('', inplace=True)
            self._date_converter(self.COLS_DATE)
        except FileNotFoundError as err:
            self.ERROR = f"FileNotFoundError: {err}"
            logger.error(self.ERROR)

    def read_all(self):
        """
        Extracting data for the table from the Database
        :return:
            list of dictionnaries that represents the data for table
        """
        data1 = []
        if not self.ERROR:
            data = [dict(self.sheet.loc[line].fillna('')) for line in range(self.nrows)]
            for row in data:
                for key, value in dict(row).items():
                    if not value:
                        del row[key]
                data1.append(row)
        return data1

    def xelon_number_list(self):
        if not self.ERROR:
            return list(self.sheet.get("numero_de_dossier", []))
        return []

    def _data_update(self):
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line]
            data.append(dict((key, value.strip()) for key, value in row.items()))
        return data
