from utils.microsoft_format import ExcelFormat


class ExcelEcuCrossReference(ExcelFormat):
    DROP_COLS = {'Brand', 'Unnamed: 7', 'Unnamed: 10', 'Unnamed: 13', 'Comparatif avec fichier fourni par  Hassan Kesssou'}

    def __init__(self, file, sheet_index=0, columns=None, skip_rows=3):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        super(ExcelEcuCrossReference, self).__init__(file, sheet_index, columns, skip_rows, dtype=str)
        self.sheet.drop(columns=self.DROP_COLS, inplace=True)
        self._columns_convert()
        self.sheet.fillna('', inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line]
            data.append(dict(row))
        return data
