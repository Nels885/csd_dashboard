import xlrd


class ExcelRaspeedi:
    """## Read data in Excel file for Raspeedi ##"""

    def __init__(self, file, sheet_index=0, columns=-3):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        self.book = xlrd.open_workbook(file)
        self.sheet = self.book.sheet_by_index(sheet_index)
        self.nrows = self.sheet.nrows
        self.columns = self.sheet.row_values(0)[:columns]

    def read(self):
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
            for i in range(4, 6):
                if row[i] == "O":
                    row[i] = True
                elif row[i] in ["N", "?", ""]:
                    row[i] = False
            row_dict = dict(zip(self.columns, row))
            data.append(row_dict)
        return data
