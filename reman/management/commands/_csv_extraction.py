from utils.microsoft_format import CsvFormat


class CsvSparePart(CsvFormat):
    SPARE_COLS = ['code_magasin', 'code_produit', 'code_zone', 'code_site', 'code_emplacement', 'cumul_dispo']

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
        super().__init__(file, columns)
        self._columns_convert()
        self.sheet.replace({"#": None}, inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            data.append(dict(self.sheet.loc[line, self.SPARE_COLS].dropna()))
        return data
