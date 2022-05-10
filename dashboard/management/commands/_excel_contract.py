import logging

from utils.microsoft_format import ExcelFormat

logger = logging.getLogger('command')


class ExcelContract(ExcelFormat):
    """## Read data in Excel file for Contract ##"""
    ERROR = False
    COLS = {'A': 'code', 'B': 'service', 'D': 'nature', 'E': 'object', 'F': 'supplier',
            'H': 'site', 'K': 'end_date', 'L': 'is_active', 'N': 'renew_date'}
    COLS_DATE = {'end_date': "%Y-%m-%d %H:%M:%S", 'renew_date': "%Y-%m-%d %H:%M:%S"}
    COLS_BOOLEAN = {'is_active': {"oui": True, "OUI": True, "Oui": True, "non": False}}

    def __init__(self, file, sheet_name=0, columns=None, skiprows=None):
        """
        Initialize ExcelContract class
        :param file:
            excel file to process
        :param sheet_name:
            Sheet index to be processed from excel file
        :param columns:
            Number of the last column to be processed
        """
        try:
            cols = ",".join(self.COLS.keys())
            super(ExcelContract, self).__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=cols)
            self.sheet.dropna(axis='columns', how='all', inplace=True)
#             self._columns_convert()
            self._columns_rename(self.COLS)
            self._date_converter(self.COLS_DATE)
            self._boolean_convert(self.COLS_BOOLEAN)
        except FileNotFoundError as err:
            logger.error(f'FileNotFoundError: {err}')
            self.ERROR = True

    def read(self):
        data = []
        if not self.ERROR:
            for line in range(self.nrows):
                try:
                    row = {'id': line}
                    row.update(dict(self.sheet.loc[line].dropna(how='all')))  # get the data in the ith row
                    data.append(row)
                except KeyError:
                    pass
        return data
