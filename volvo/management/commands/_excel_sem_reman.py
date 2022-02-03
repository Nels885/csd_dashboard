from utils.microsoft_format import ExcelFormat


class ExcelSemRefBase(ExcelFormat):
    COLS = {'A': 'brand', 'B': 'map_data', 'C': 'product_part', 'D': 'reman_reference',
            'E': 'pf_code', 'F': 'asm_reference', 'G': 'hw_reference', 'H': 'asm_oe', 'I': 'vehicle',
            'J': 'core_part', 'K': 'pf_code_oe', 'L': 'pi_code_oe', 'M': 'fan', 'N': 'rear_bolt', 'O': 'hw_oe'}

    def __init__(self, file, sheet_name=0, columns=None, skiprows=1):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        cols = ",".join(self.COLS.keys())
        super().__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=cols)
        self._columns_rename(self.COLS)
        self.sheet.replace({"#": None}, inplace=True)
        self.sheet.fillna('', inplace=True)
        self.data = self._data_update()

    def read_all(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        return self.data

    def _dict(self, row, keys):
        data_dict = {}
        for key in list(keys):
            data_dict.update({key: row[key].strip()})
        return data_dict

    def _data_update(self):
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line]
            data.append(dict((key, value.strip()) for key, value in row.items()))
        return data
