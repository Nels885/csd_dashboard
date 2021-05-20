from utils.microsoft_format import ExcelFormat


class ExcelEcuCrossReference(ExcelFormat):
    DROP_COLS = {'Brand', 'Unnamed: 7', 'Unnamed: 10', 'Unnamed: 13',
                 'Comparatif avec fichier fourni par  Hassan Kesssou'}

    def __init__(self, file, sheet_name=0, columns=None, skiprows=3):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        super(ExcelEcuCrossReference, self).__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=None)
        self.sheet.drop(columns=self.DROP_COLS, inplace=True)
        self._columns_convert()
        self.sheet.fillna('', inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            row = self.sheet.loc[line]
            data.append(dict(row))
        return data


class ExcelEcuRefBase(ExcelFormat):
    COLS = {'A': 'oe_raw_reference', 'B': 'reman_reference', 'C': 'technical_data', 'D': 'hw_reference',
            'E': 'supplier_oe', 'F': 'psa_barcode', 'G': 'former_oe_reference', 'H': 'ref_cal_out', 'I': 'code_produit',
            'J': 'ref_psa_out', 'K': 'req_diag', 'L': 'open_diag', 'M': 'req_ref', 'N': 'ref_mat', 'O': 'ref_comp',
            'P': 'req_cal', 'Q': 'cal_ktag', 'R': 'req_status', 'S': 'status', 'T': 'test_clear_memory',
            'U': 'cle_appli'}

    def __init__(self, file, sheet_name=0, columns=None, skiprows=None):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        cols = ",".join(self.COLS.keys())
        super(ExcelEcuRefBase, self).__init__(file, sheet_name, columns, skiprows, dtype=str, usecols=cols)
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

    def part_base_model(self):
        data = []
        part_list = ['code_produit']
        base_list = ['reman_reference']
        model_list = [
            'psa_barcode', 'oe_raw_reference', 'technical_data', 'hw_reference', 'supplier_oe', 'former_oe_reference'
        ]
        for row in self.data:
            part_dict = self._dict(row, part_list)
            base_dict = self._dict(row, base_list)
            model_dict = self._dict(row, model_list)
            data.append({'part': part_dict, 'base': base_dict, 'model': model_dict})
        return data

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
