from utils.excel_format import ExcelFormat


class ExcelRaspeedi(ExcelFormat):
    """## Read data in Excel file for Raspeedi ##"""

    def __init__(self, file, sheet_index=0, columns=12):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        super().__init__(file, sheet_index, columns)
        self._convert_boolean()

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            try:
                row = list(self.sheet.loc[line, self.columns])  # get the data in the ith row
                row_dict = dict(zip(self.columns, row))
                data.append(row_dict)
            except KeyError as err:
                print("KeyError pour la ligne : {}".format(err))
        return data

    def _convert_boolean(self):
        """
        Converting string values 'O' or 'N' in boolean
        :return:
            Data line converts
        """
        for col in ["dab", "cam"]:
            self.sheet[col] = self.sheet[col].replace({"O": True, "N": False, "?": False, "": False})
