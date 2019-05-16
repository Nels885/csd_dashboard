import pandas as pd
import unicodedata


class ExcelSqualaetp:
    """## Read data in Excel file for Squalaetp ##"""

    def __init__(self, file, sheet_index=0, columns=-1):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        df = pd.read_excel(file, sheet_index, na_values='#')
        df.dropna(how='all', inplace=True)
        self.sheet = df.fillna('')
        self.nrows = self.sheet.shape[0] - 1
        self.columns = list(self.sheet.columns[:columns])

    def read_all(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            if line == 0:
                continue  # ignore the first row
            row = self.sheet.row_values(line)  # get the data in the ith row
            row_dict = dict(zip(self.columns, row))
            data.append(row_dict)
        return data

    def read_xelon(self):
        xelon_columns = ['Numéro de dossier', 'V.I.N.', 'Modèle produit', 'Modèle véhicule']
        data = []
        for line in range(self.nrows):
            if line == 0:
                continue  # ignore the first row
            row = list(self.sheet.loc[line, xelon_columns])  # get the data in the ith row
            row_dict = dict(zip(self._columns_convert(xelon_columns), row))
            data.append(row_dict)
        return data

    @staticmethod
    def _columns_convert(columns):
        data = []
        deletion = {' ': '_', '.': ''}
        for column in columns:
            name = unicodedata.normalize('NFKD', column).encode('ASCII', 'ignore').decode('utf8').lower()
            for old, new in deletion.items():
                name = name.replace(old, new)
            data.append(name)
        return data
