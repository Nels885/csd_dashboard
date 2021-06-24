from utils.microsoft_format import ExcelFormat, pd


class ExcelCorvet(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""

    CORVET_DROP_COLS = ['numero_de_dossier', 'modele_produit', 'modele_vehicule']
    COLS_DATE = {'date_debut_garantie': "%d/%m/%Y %H:%M:%S", 'date_entree_montage': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, attribut_file=None, sheet_name=0, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super(ExcelCorvet, self).__init__(file, sheet_name, columns, dtype=str)
        self._columns_convert()
        self.sheet.replace({"#": None}, inplace=True)
        self._date_converter(self.COLS_DATE)
        df_corvet = self.sheet.drop(self.CORVET_DROP_COLS, axis='columns')
        self.sheet, self.nrows = self._add_attributs(df_corvet, attribut_file)

    def read(self):
        """
        Extracting data for the Corvet table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet table
        """
        data = []
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
        for row in self.read():
            vin = row['vin']
            data.append({'vin': vin, 'data': row})
        return data
