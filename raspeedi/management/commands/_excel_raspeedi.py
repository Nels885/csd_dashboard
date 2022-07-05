from utils.microsoft_format import ExcelFormat


class ExcelRaspeedi(ExcelFormat):
    """## Read data in Excel file for Raspeedi ##"""
    COLS = {'A': 'ref_boitier', 'B': 'produit', 'C': 'facade', 'D': 'type', 'E': 'dab', 'F': 'cam', 'G': 'dump_peedi',
            'H': 'cd_version', 'I': 'media', 'J': 'carto', 'K': 'dump_renesas', 'L': 'ref_mm', 'N': 'jukebox'}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        cols = ",".join(self.COLS.keys())
        super(ExcelRaspeedi, self).__init__(file, sheet_name, columns, dtype=str, usecols=cols)
        self._convert_boolean()
        self._columns_rename(self.COLS)
        self._drop_lines()
        self.sheet.fillna('', inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            try:
                data.append(dict(self.sheet.loc[line]))
            except KeyError as err:
                print("KeyError pour la ligne : {}".format(err))
        return data

    def _convert_boolean(self):
        """
        Converting string values 'O' or 'N' in boolean
        :return:
            Data line converts
        """
        for col in ["dab", "cam", "JUKEBOX"]:
            self.sheet[col] = self.sheet[col].replace({
                "O": True, "N": False, "?": False, None: False, "NON": False, "OUI": True
            })

    def _drop_lines(self):
        df = self.sheet
        self.sheet = df.drop(df[(df[self.COLS['A']].isnull()) | (df[self.COLS['A']] == 'ref_boitier')].index)
        self.sheet.reset_index(drop=True, inplace=True)
        self.nrows = self.sheet.shape[0]


class ExcelPrograming(ExcelFormat):
    """## Read data in Excel file for Raspeedi ##"""
    COLS = {'A': 'psa_barcode', 'B': 'peedi_path', 'G': 'peedi_dump', 'K': 'renesas_dump'}

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        cols = ",".join(self.COLS.keys())
        super(ExcelPrograming, self).__init__(file, sheet_name, columns, dtype=str, usecols=cols)
        self._columns_rename(self.COLS)
        self._drop_lines()
        self.sheet.fillna('', inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        data = []
        for line in range(self.nrows):
            try:
                data.append(dict(self.sheet.loc[line]))
            except KeyError:
                print("KeyError: {}".format(line))
        #         return [dict(self.sheet.loc[line]) for line in range(self.nrows)]
        return data

    def _drop_lines(self):
        df = self.sheet
        self.sheet = df.drop(df[(df[self.COLS['A']].isnull()) | (df[self.COLS['A']] == 'psa_barcode')].index)
        self.sheet.reset_index(drop=True, inplace=True)
        self.nrows = self.sheet.shape[0]
