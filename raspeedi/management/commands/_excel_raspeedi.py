import pandas as pd


class ExcelRaspeedi:
    """## Read data in Excel file for Raspeedi ##"""

    def __init__(self, file, sheet_index=0, columns=-3):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        df = pd.read_excel(file, sheet_index, converters={'ref_boitier': int, 'cd_version': str})
        df.dropna(how='all', inplace=True)
        self.sheet = df.fillna('')
        self.nrows = self.sheet.shape[0] - 1
        self.columns = list(self.sheet.columns[:columns])

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            row = list(self.sheet.loc[line, self.columns])  # get the data in the ith row
            row = self._convert_boolean(row)
            row_dict = dict(zip(self.columns, row))
            data.append(row_dict)
        return data

    @staticmethod
    def _convert_boolean(row):
        """
        Converting string values 'O' or 'N' in boolean
        :param row:
            Data line
         :return:
            Data line converts
        """
        for i in range(4, 6):
            if row[i] == "O":
                row[i] = True
            elif row[i] in ["N", "?", ""]:
                row[i] = False
        return row
