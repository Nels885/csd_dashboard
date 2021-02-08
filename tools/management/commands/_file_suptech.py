from utils.microsoft_format import CsvFormat, ExcelFormat, pd


class CsvSuptech(CsvFormat):
    COLS = {"DATE": "date", "QUI": "user", "XELON": "xelon", "ITEM": "item", "TIME": "time", "INFO": "info",
            "RMQ": "rmq"}
    COLS_DATE = {'date': "%d/%m/%Y"}

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
        try:
            super(CsvSuptech, self).__init__(file, columns, dtype=str, usecols=self.COLS.keys())
            self._columns_rename(self.COLS)
            self.sheet.replace({"": None}, inplace=True)
            self._date_converter(self.COLS_DATE)
            self.error = False
        except pd.errors.EmptyDataError:
            self.error = True

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        if not self.error:
            for line in range(self.nrows):
                data.append(dict(self.sheet.loc[line].dropna()))
        return data


class ExcelSuptech(ExcelFormat):
    """## Read data in Excel file for LOG_SUPTECH.xlsx ##"""
    COLS = {"DATE": "date", "QUI": "user", "XELON": "xelon", "ITEM": "item", "TIME": "time", "INFO": "info",
            "RMQ": "rmq", "ACTION/RETOUR": "action"}
    COLS_DATE = {'date': "%d/%m/%Y %H:%M:%S"}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelSqualaetp class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        super(ExcelSuptech, self).__init__(file, sheet_name, columns)
        self._columns_rename(self.COLS)
        self.sheet.replace({"": None}, inplace=True)
        self._date_converter(self.COLS_DATE)

    def read(self):
        """
        Extracting data for the Suptech table form the Database
        :return:
            list of dictionnaries that represents the data for Suptech table
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line]  # get the data in the ith row
            data.append(dict(row.dropna()))
        return data
