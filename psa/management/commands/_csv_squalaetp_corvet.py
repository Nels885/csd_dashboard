from utils.microsoft_format import CsvFormat


class CsvCorvet(CsvFormat):
    COLS_DATE = {'donnee_date_debut_garantie': "%d/%m/%Y %H:%M:%S", 'donnee_date_entree_montage': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_index:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super().__init__(file, columns, dtype='str')
        self._columns_convert()
        self.sheet.replace({"#": None}, inplace=True)
        self._date_converter(self.COLS_DATE)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            data.append(dict(self.sheet.loc[line].dropna()))
        return data
