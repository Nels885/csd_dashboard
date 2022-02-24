import tempfile
import datetime
import csv
import os.path

from django.utils import timezone
from celery_progress.backend import ProgressRecorder
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from sbadmin.tasks.base import BaseTask
from utils.file.export import HTMLFilter, re


class ExportExcelTask(BaseTask):
    name = "ExportExcelTask"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.date = timezone.now()
        self.sheetName = kwargs.get('sheet_name', 'Feuil1')
        self.noValue = kwargs.get('novalue', "#")
        self.header = self.fields = []
        self.textCols = kwargs.get('text_cols', [])

    @staticmethod
    def copy_and_get_copied_path():
        destination_path = "%s" % (tempfile.gettempdir())
        return destination_path

    @staticmethod
    def get_header_fields(prod_list):
        header = [value_tuple[0] for value_tuple in prod_list]
        fields = [value_tuple[1] for value_tuple in prod_list]
        return header, fields

    def file(self, filename, excel_type, values_list):
        """
        Creation file
        :param filename: file name
        :param excel_type: type of Excel file (xls, xlsx, csv)
        :param values_list: List of values to include in the file
        :return Destination path to file
        """
        path = self.copy_and_get_copied_path()
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        if excel_type == "csv":
            self._create_csv(destination_path, self.header, values_list)
        else:
            workbook = Workbook()
            workbook = self._create_workbook(workbook, self.header, values_list)
            workbook.save(filename=destination_path)
        return destination_path

    def _create_workbook(self, workbook: Workbook, header, values_list):
        """ Formatting data in Excel 2010 format """
        progress_recorder = ProgressRecorder(self)
        # Get active worksheet/tab
        ws = workbook.active
        ws.title = self.sheetName

        # Sheet header, first row
        row_num = 1
        total_record = len(values_list)

        # Assign the titles for each cell of the header
        for col_num, column_title in enumerate(header, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.font = Font(bold=True)
            cell.value = column_title

        # Iterate though all values
        for query in values_list:
            row_num += 1
            query = tuple([self._html_to_string(_) if isinstance(_, str) else _ for _ in query])
            query = self._query_format(query)

            # Assign the data  for each cell of the row
            for col_num, cell_value in enumerate(query, 1):
                cell = ws.cell(row=row_num, column=col_num)
                if col_num in self.textCols:
                    cell.alignment = Alignment(wrapText=True)
                cell.value = cell_value
            progress_recorder.set_progress(row_num + 1, total=total_record, description="Inserting record into row")
        return workbook

    def _create_csv(self, filename, header, values_list):
        """ Formatting data in CSV format """
        progress_recorder = ProgressRecorder(self)
        total_record = len(values_list)
        with open(filename, 'w+', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';', lineterminator=';\r\n')
            writer.writerow(header)

            for row_num, query in enumerate(values_list):
                query = tuple([self._html_to_string(_, r'[;,]') if isinstance(_, str) else _ for _ in query])
                query = self._query_format(query)
                writer.writerow(query)
                progress_recorder.set_progress(row_num + 1, total=total_record, description="Inserting record into row")

    def _query_format(self, query):
        format_date = "%d/%m/%Y %H:%M:%S"
        query = tuple(
            [_.strftime(format_date).replace(" 00:00:00", "") if isinstance(_, datetime.date) else _ for _ in query]
        )
        query = tuple([self.noValue if not value else value for value in query])
        return query

    @staticmethod
    def _html_to_string(value, re_sub=None):
        f = HTMLFilter()
        f.feed(value)
        if re_sub:
            return re.sub(re_sub, ' ', f.text)
        else:
            return f.text
