import tempfile
import datetime

from django.utils import timezone
from celery_progress.backend import ProgressRecorder
from openpyxl import Workbook
from openpyxl.styles import Font

from sbadmin.tasks.base import BaseTask
from utils.file.export import HTMLFilter, re


class ExportExcelTask(BaseTask):
    name = "ExportExcelTask"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.date = timezone.now()
        self.noValue = "#"
        self.header = self.fields = []

    def copy_and_get_copied_path(self):
        destination_path = "%s" % (tempfile.gettempdir())
        return destination_path

    def create_workbook(self, workbook: Workbook, header, values_list):
        """ Formatting data in Excel 2010 format """
        progress_recorder = ProgressRecorder(self)
        # Get active worksheet/tab
        ws = workbook.active
        ws.title = 'Feuille 1'

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
                cell.value = cell_value
            progress_recorder.set_progress(row_num + 1, total=total_record, description="Inserting record into row")
        return workbook

    # def _csv_writer(self, response):
    #     """ Formatting data in CSV format """
    #     writer = csv.writer(response, delimiter=';', lineterminator=';\r\n')
    #     writer.writerow(self.header)
    #
    #     for i, query in enumerate(self.valueSet):
    #         query = tuple([self._html_to_string(_, r'[;,]') if isinstance(_, str) else _ for _ in query])
    #         query = self._query_format(query)
    #         writer.writerow(query)

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
