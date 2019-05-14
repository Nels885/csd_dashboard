import xlrd
import unicodedata


class ExcelSqualaetp:
    """## Read data in Excel file for Squalaetp ##"""

    def __init__(self, file, sheet_index=0, columns=-1):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        self.book = xlrd.open_workbook(file)
        self.sheet = self.book.sheet_by_index(sheet_index)
        self.nrows = self.sheet.nrows
        self.columns = self.sheet.row_values(0)[:columns]
        # self.columns = []
        # for column in columns:
        #     name = unicodedata.normalize('NFKD', column).encode('ASCII', 'ignore')
        #     self.columns.append(name.decode('utf8').replace(' ', '_').replace('.', '').lower())

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
        columns = ['numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule']
        data = []
        for line in range(self.nrows):
            if line == 0:
                continue  # ignore the first row
            row = self.sheet.row_values(line)  # get the data in the ith row
            row_dict = dict(zip(columns, row))
            data.append(row_dict)
        return data
