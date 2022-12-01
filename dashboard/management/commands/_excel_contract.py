import logging

from utils.microsoft_format import ExcelFormat
from utils.file.export_task import ExportExcel, datetime

logger = logging.getLogger('command')


class ExcelContract(ExcelFormat):
    """## Read data in Excel file for Contract ##"""
    ERROR = False
    COLS = {'A': 'code', 'B': 'service', 'D': 'nature', 'E': 'object', 'F': 'supplier',
            'H': 'site', 'K': 'end_date', 'L': 'is_active', 'N': 'renew_date'}
    COLS_DATE = {'end_date': "%Y-%m-%d %H:%M:%S", 'renew_date': "%Y-%m-%d %H:%M:%S"}
    COLS_BOOLEAN = {'is_active': {"oui": True, "OUI": True, "Oui": True, "non": False}}

    def __init__(self, file, sheet_name=1, columns=None, skiprows=None):
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
                    row = {'id': (line + 1)}
                    row.update(dict(self.sheet.loc[line].dropna(how='all')))  # get the data in the ith row
                    data.append(row)
                except KeyError:
                    pass
        return data


class ExportExcelContract(ExportExcel):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _query_format(self, query):
        query = tuple([self._html_to_string(_) if isinstance(_, str) else _ for _ in query])
        query = tuple([self._timestamp_to_string(_) for _ in query])
        query = tuple([self._boolean_to_string(_) for _ in query])
        return query

    @staticmethod
    def _boolean_to_string(value):
        if isinstance(value, bool) and value is True:
            return "OUI"
        elif isinstance(value, bool) and value is False:
            return ""
        return value

    @staticmethod
    def _timestamp_to_string(value):
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y/%m/%d %H:%M:%S").replace(" 00:00:00", "")
        elif isinstance(value, datetime.date):
            value = value.strftime("%Y/%m/%d")
        elif isinstance(value, datetime.time):
            value = value.strftime("%H:%M:%S")
        return value
