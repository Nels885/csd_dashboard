from utils.microsoft_format import ExcelFormat


class ExcelUserSkill(ExcelFormat):
    """## Read data in Excel file for Squalaetp ##"""

    def __init__(self, file, sheet_name, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super(ExcelUserSkill, self).__init__(file, sheet_name, columns, skiprows=7)
        self.sheet.drop(self.sheet.columns[[0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]], axis=1, inplace=True)
        self._drop_columns()
        self.sheet = self.sheet.set_index('product').transpose().reset_index().rename(columns={'index': 'Nom'})
        self.nrows = self.sheet.shape[0]

    def read(self):
        data = []
        for line in range(self.nrows):
            try:
                row = self.sheet.loc[line]  # get the data in the ith row
                data.append(dict(row.dropna(how='all')))
            except KeyError:
                pass
        return data

    def _drop_columns(self):
        for column in self.columns:
            if "Employé" in column:
                del self.sheet[column]
        self.sheet.rename(columns={'Unnamed: 1': 'product'}, inplace=True)
