from utils.microsoft_format import ExcelFormat


class ExcelRaspeedi(ExcelFormat):
    """## Read data in Excel file for Raspeedi ##"""
    RASPEEDI_COLS = ['ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'dump_peedi', 'cd_version', 'media',
                     'carto', 'dump_renesas', 'ref_mm']

    def __init__(self, file, sheet_name=0, columns=None):
        """
        Initialize ExcelRaspeedi class
        :param file:
            excel file to process
        """
        super(ExcelRaspeedi, self).__init__(file, sheet_name, columns, dtype=str)
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
                data.append(dict(self.sheet.loc[line, self.RASPEEDI_COLS].dropna()))
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
            self.sheet[col] = self.sheet[col].replace({"O": True, "N": False, "?": False, None: False})


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
        self._columns_rename()
        self.sheet.fillna('', inplace=True)

    def read(self):
        """
        Formatting data from the Raspeedi excel file
        :return:
            list of dictionnaries that represents the data in the sheet
        """
        return [dict(self.sheet.loc[line]) for line in range(self.nrows)]

    def _columns_rename(self):
        new_columns = {}
        for i, column in enumerate(self.columns):
            new_columns[column] = list(self.COLS.values())[i]
        self.sheet.rename(columns=new_columns, inplace=True)
        self.columns = list(self.sheet.columns)
