from utils.microsoft_format import ExcelFormat, re, pd


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
        :param sheet_index:
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
            data.append(dict(self.sheet.loc[line, self.XELON_COLS].dropna()))
        return data

    def corvet_table(self, attribut_file):
        """
        Extracting data for the Corvet table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet table
        """
        data = []
        df_corvet = self.sheet.drop(self.CORVET_DROP_COLS, axis='columns').fillna("")
        if attribut_file:
            df_attributs = pd.read_excel(attribut_file, 1, converters={'cle2': str})
            self._add_attributs(df_corvet, df_attributs)
        for line in range(self.nrows):
            df_corvet = self.sheet.drop(self.CORVET_DROP_COLS, axis='columns')
            row = df_corvet.loc[line]  # get the data in the ith row
            if re.match(r'^VF[37]\w{14}$', str(row[0])) and row[2] != '':
                data.append(dict(row.dropna()))
        return data

    def corvet_backup_table(self):
        """
        Extracting data for the Corvet Backup table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet Backup table
        """
        return self.corvet_table(None)

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
