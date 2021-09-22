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
        super(ExcelUserSkill, self).__init__(file, sheet_name, columns, skiprows=5)
        self.sheet.drop(self.sheet.columns[[0]], axis=1, inplace=True)

    def read(self):
        """
        Extracting data for the Corvet table form the Database
        :return:
            list of dictionnaries that represents the data for Corvet table
        """
        data = []
        for line in range(self.nrows):
            try:
                row = self.sheet.loc[line]  # get the data in the ith row
                data.append(dict(row.dropna()))
            except KeyError:
                pass
        return data
