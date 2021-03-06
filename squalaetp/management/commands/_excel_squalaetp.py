from utils.microsoft_format import ExcelFormat, pd


class ExcelSqualaetp(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""

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
        super(ExcelSqualaetp, self).__init__(file, sheet_name, columns)
        self._columns_convert()
        self.sheet.replace({"#": None}, inplace=True)
        self._date_converter(self.COLS_DATE)

    def xelon_table(self):
        """
        Extracting data for the Xelon table from the Database
        :return:
            list of dictionnaries that represents the data for Xelon table
        """
        data = []
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
        for row in self.corvet_table():
            vin = row['vin']
            data.append({'vin': vin, 'data': row})
        return data
