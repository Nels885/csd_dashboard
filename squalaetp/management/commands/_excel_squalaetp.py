from utils.excel_format import ExcelFormat, re, pd


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
